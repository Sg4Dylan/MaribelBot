import os
import json
import uuid
import random
import requests
import configparser
import xml.etree.cElementTree as ET
import subprocess
from tgfunc import *

headers = {
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
    'DNT': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2873.0 Safari/537.36',
}

def five_in_one(update: dict) -> bool:
    
    # 站点类型
    site_type = 0
    # 用户输入标签
    tag_list = []
    # 图片过滤：全部/纵版/横版
    screen_type = 0
    # API URL
    source_url = ""
    # API 返回 RAW
    api_ret = ""
    # API 返回
    result_json = []
    xml_to_list = []
    # 随机数
    random_img_id = 0
    # 图片图示
    caption_text = ""
    # 显示样图 URL
    img_sample_url = ""
    # 原始图 URL
    img_file_url = ""
    # 下载使用的 URL
    download_url = ""
    # 图片 ID
    img_id = ""
    # 图片文件名
    download_img_name = ""
    # 下载失败标记
    download_fail_flag = False
    # 重新发送标记
    retry_send_flag = False
    # 图片尺寸
    img_size = ""
    # 安全 roll
    config_file_path = "./db/safemode.ini"
    # HD Mode
    hd_mode_config = "./db/hdmode.ini"
    
    def init_site_type():
        nonlocal site_type
        request_text = update['message'].get('text','')
        if 'http' in request_text:
            return False
        if request_text.startswith('/yandere'):
            site_type = 0
        elif request_text.startswith('/konachan'):
            site_type = 1
        elif request_text.startswith('/danbooru'):
            site_type = 2
        elif request_text.startswith('/3dbooru'):
            site_type = 3
        elif request_text.startswith('/gelbooru'):
            site_type = 4
        else:
            return False
        return True
    
    def init_tag():
        nonlocal tag_list
        # 分离参数
        try:
            tag_list.append(update['message'].get('text','').split(' ', 1)[1])
        except IndexError:
            tag_list.append(' ')
    
    def init_api_url():
        nonlocal site_type, tag_list, source_url
        # 构造API URL
        random_page_id = 1
        if tag_list[0] == " ":
            random_page_id = str(random.randint(1, 10))
            if site_type == 3:
                random_page_id = str(random.randint(1, 1000))
        if site_type == 0:
            source_url = "https://yande.re/post.json?limit=100&page=%s&tags=%s" \
                         % (random_page_id, tag_list[0])
        elif site_type == 1:
            source_url = "https://konachan.com/post.json?limit=100&page=%s&tags=%s" \
                         % (random_page_id, tag_list[0])
        elif site_type == 2:
            source_url = "https://danbooru.donmai.us/posts.json?limit=100&page=%s&tags=%s" \
                         % (random_page_id, tag_list[0])
        elif site_type == 3:
            source_url = "http://behoimi.org/post/index.json?limit=100&page=%s&tags=%s" \
                         % (random_page_id, tag_list[0])
        elif site_type == 4:
            source_url = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&limit=100&pid=%s&tags=%s" \
                         % (random_page_id, tag_list[0])
        else:
            return False
        return True
    
    def screen_type_init():
        nonlocal screen_type
        if "#vertical" in update['message'].get('text',''):
            screen_type = 1
        elif "#horizontal" in update['message'].get('text',''):
            screen_type = 2
        else:
            pass
    
    def call_api():
        nonlocal site_type, source_url, result_json, xml_to_list, api_ret
        try:
            if site_type != 4:
                api_ret = requests.get(source_url, headers=headers).content.decode(encoding='UTF-8')
                result_json = json.loads(api_ret)
            else:
                api_ret = requests.get(source_url, headers=headers).content.decode(encoding='UTF-8')
                xml_fetch_root = ET.fromstring(api_ret)
                for child in xml_fetch_root:
                    xml_to_list.append(child.attrib)
        except Exception as e:
            logger.error(f'Call IMG API ERROR: {e}')
    
    def check_api_result():
        # 探测抓取结果
        nonlocal result_json, xml_to_list, site_type
        if str(result_json) == "[]" and site_type != 4:
            send_message(update, True, "十分抱歉，您查找的_tag_并没有结果")
            send_sticker(update, 'BQADBQADtgEAAnVo_QMW7xR_mxZf8wI')
            return False
        if not xml_to_list and site_type == 4:
            if "API disabled" in api_ret:
                send_message(update, True, "因遭到滥用，目标站点已关闭搜索 API，恢复时间未知")
                send_sticker(update, 'CAADBQAD2AAD7zZ-AhmElS0mPhgeAg')
            else:
                send_message(update, True, "十分抱歉，您查找的_tag_并没有结果")
                send_sticker(update, 'BQADBQADtgEAAnVo_QMW7xR_mxZf8wI')
            return False
        return True
    
    def filter_result():
        nonlocal result_json, xml_to_list, site_type
        st_result = []
        sm_result = []
        # 过滤 screen type
        logger.debug("[ScreenType] start resolution filter.")
        input_result = xml_to_list if site_type == 4 else result_json
        for item in input_result:
            if screen_type_check(item):
                st_result.append(item)
        if not st_result:
            send_message(update, True, "十分抱歉，您请求的排版类型并没有结果")
            return False
        # 过滤 safe mode
        logger.debug("[SafeModule] start safe filter.")
        for item in st_result:
            if safe_module_filter(item):
                sm_result.append(item)
        if not sm_result:
            send_message(update, True, "出于当前安全设定考虑，您请求内容已被阻止")
            return False
        if site_type == 4:
            xml_to_list = sm_result
        else:
            result_json = sm_result
        return True
    
    # 分辨率排版测定
    def screen_type_check(item):
        nonlocal screen_type, site_type
        final_result = False
        
        def parse_resolution():
            if site_type == 2:
                s_width = item['image_width']
                s_height = item['image_height']
            else:
                s_width = item['sample_width']
                s_height = item['sample_height']
            if s_width == s_height:
                return 0
            return 1 if s_width<s_height else 2
        
        def compare_result():
            parse_result = parse_resolution()
            if parse_result == 0:
                return True
            if screen_type == parse_result:
                return True
            else:
                return False
        
        if screen_type == 0:
            return True
        return compare_result()
    
    # 全年龄过滤
    def safe_module_filter(item):
        nonlocal config_file_path
        
        def safe_status():
            config_ins = configparser.ConfigParser()
            config_ins.read(config_file_path)
            return config_ins.getboolean('SafeModule', str(update['message']['chat']['id']), fallback=False)
        
        if not safe_status():
            return True
        if item["rating"] == "s":
            return True
        else:
            return False
    
    def prepare_random_id():
        # 准备随机数
        nonlocal site_type, random_img_id, xml_to_list, result_json
        if not filter_result():
            return False
        if site_type == 4:
            random_img_id = random.randint(0, len(xml_to_list) - 1)
        else:
            random_img_id = random.randint(0, len(result_json) - 1)
        return True
    
    def prepare_info():
        # 设定提示语
        nonlocal site_type, caption_text
        if site_type == 0:
            caption_text = 'Yandere ID: '
        elif site_type == 1:
            caption_text = 'Konachan ID: '
        elif site_type == 2:
            caption_text = 'Danbooru ID: '
        elif site_type == 3:
            caption_text = '3dbooru ID: '
        elif site_type == 4:
            caption_text = 'Gelbooru ID: '
        else:
            return False
        return True
    
    def prepare_img_link():
        nonlocal site_type, img_sample_url, img_file_url, download_url, result_json, xml_to_list, random_img_id
        if not prepare_random_id():
            return False
        
        def hd_status():
            config_ins = configparser.ConfigParser()
            config_ins.read(hd_mode_config)
            return config_ins.getboolean('HD-Mode', str(update['message']['chat']['id']), fallback=False)
        
        # 设定图片链接
        if site_type == 2:
            img_sample_url =result_json[random_img_id].get('file_url','')
            img_file_url = result_json[random_img_id]["large_file_url"]
            if not 'https://danbooru.donmai.us' in img_sample_url:
                img_sample_url = "https://danbooru.donmai.us" + img_sample_url
            if not 'https://danbooru.donmai.us' in img_file_url:
                img_file_url = "https://danbooru.donmai.us" + img_file_url
        elif site_type == 3:
            if 'twimg.com' in result_json[random_img_id]["source"]:
                result_json[random_img_id]["source"] = ''
            if result_json[random_img_id]["source"] != "":
                img_sample_url = result_json[random_img_id]["source"]
                img_file_url = result_json[random_img_id]["source"]
            else:
                img_sample_url = result_json[random_img_id]["sample_url"]
                img_file_url = "http://behoimi.org/post/show/" + str(result_json[random_img_id]["id"])
        elif site_type == 4:
            img_sample_url = xml_to_list[random_img_id]['sample_url']
            img_file_url = xml_to_list[random_img_id].get('file_url','')
            if not 'https:' in img_sample_url:
                img_sample_url = 'https:' + img_sample_url
            if not 'https:' in img_file_url:
                img_file_url = 'https:' + img_file_url
        else:
            img_sample_url = result_json[random_img_id]["sample_url"]
            img_file_url = result_json[random_img_id].get('file_url','')
        # 检测地址并补全 - For konachan
        if img_sample_url.startswith("//"):
            img_sample_url = "https:" + img_sample_url
        if img_file_url.startswith("//"):
            img_file_url = "https:" + img_file_url
        
        # HD-Mode 图片切换
        download_url = img_sample_url
        if hd_status():
            logger.debug("[HD-Mode] HD mode enable.")
            # 准备 HD 图链接
            hd_img_url = img_file_url
            if site_type == 3:
                if result_json[random_img_id]["source"] == '':
                    hd_img_url = result_json[random_img_id].get('file_url','')
            # 确认并替换
            if hd_img_url != '':
                download_url = hd_img_url
            else:
                logger.debug("[HD-Mode] HD image url error.")
        
        return True
    
    # 随机取出图片 ID
    def prepare_img_id():
        nonlocal site_type, img_id, xml_to_list, result_json, random_img_id
        if site_type == 4:
            img_id = str(xml_to_list[random_img_id]['id'])
        else:
            img_id = str(result_json[random_img_id]["id"])
    
    # 执行下载
    def download_fin_img():
        nonlocal download_img_name, result_json, random_img_id, download_url
        
        def exec_cmd(cmd):
            # 执行
            success_flag = True
            nano_msg = ''
            try:
                exec_result = subprocess.check_output(
                    cmd,
                    stderr=open(os.devnull, 'w'),
                    shell=True)
                logger.info(f'Command result: {exec_result}')
            except OSError:
                logger.critical("CurlExecMemoryError")
            except Exception as e:
                logger.error(f"CurlError:{e}")
                success_flag = False
            return success_flag, nano_msg
        
        # 下载图片
        download_img_name = str(uuid.uuid4()) + '.jpg'
        curl_command = "curl -o " + download_img_name + \
                       " -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
                       "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2906.0 Safari/537.36' "
        if site_type == 3:
            curl_command = curl_command + "--referer " + "http://behoimi.org/post/show/" + \
                           str(result_json[random_img_id]["id"]) + " "
        final_command = curl_command + download_url
        logger.debug("[Debug: curl command] %s" % final_command)
        # 执行
        err_count = 0
        err_msg = ''
        while err_count < 3:
            s_flag, err_msg = exec_cmd(final_command)
            if s_flag:
                return
    
    # 检查下载结果
    def check_download_result():
        nonlocal img_size, download_img_name, download_img_name, random_img_id, caption_text
        download_img_size = 0
        try:
            download_img_size = os.path.getsize(download_img_name)
        except:
            download_fail_flag = True
        if download_img_size == 44020:
            download_fail_flag = True
        if site_type == 4:
            img_size = str(round(download_img_size / 1024, 2))
        else:
            img_size = str(round(result_json[random_img_id]["file_size"] / 1024, 2))
    
    # 发送图片
    def send_img_result():
        nonlocal caption_text, img_id, download_img_name, img_size, img_sample_url, img_file_url, download_url, retry_send_flag
        logger.debug("[Debug: file info] %s / %s" % (download_img_name,img_size))
        # 移除临时文件
        def remove_temp_file():
            try:
                os.remove(download_img_name)
            except:
                logger.debug("File might not exist.")
        
        # 发送图片 + 发送按钮
        logger.debug("[Image send Function] Ready to send photo")
        button_dict = {
            'inline_keyboard': [[{
                'text': "查看原图",
                'url': img_file_url,
            },{
                'text': "再来一张",
                'callback_data': update['message'].get('text','')
            }]],
        }
        # 检查发送结果
        if not download_fail_flag:
            send_typing(update, "upload_photo")
            sent_caption = "%s%s File size: %s KiB" % (caption_text, img_id, img_size)
            if update.get('callback_query', False):
                sent_caption = "%s%s File size: %s KiB User: %d" % (caption_text, img_id, img_size, update['from']['id'])
            sent_result = send_photo(
                update=update,
                caption=sent_caption,
                keyboard_map=button_dict,
                photo_handle=open(download_img_name, 'rb')
            )
            # 解析发送结果
            photo_too_large_flag = False
            raw_result = sent_result.content.decode('UTF-8')
            logger.debug("[Debug: result raw] %s" % sent_result.content)
            # 检查是否图片过大
            if '413 Request Entity Too Large' in raw_result:
                photo_too_large_flag = True
                remove_temp_file()
            else:
                sent_result_json = json.loads(raw_result)
                if not sent_result_json.get("ok",''):
                    remove_temp_file()
                if "PHOTO_INVALID_DIMENSIONS" in sent_result_json.get("description",''):
                    photo_too_large_flag = True
            # fallback 递归到缩略图重新发送
            if photo_too_large_flag:
                if not retry_send_flag:
                    logger.debug("[HD-Mode] Fallback to normal mode.")
                    retry_send_flag = True
                    download_url = img_sample_url
                    download_fin_img()
                    check_download_result()
                    send_img_result()
                    return True
                else:
                    logger.debug("[Debug: fail] %s" % img_file_url)
                    send_message(update, True, "图片发送过程出现故障")
        else:
            logger.debug("[Debug: fail] %s" % img_file_url)
            send_message(update, True, "图片下载过程出现故障")
        # 清除图片临时文件
        remove_temp_file()
        return True
    
    try:
        if not init_site_type():
            return False
        init_tag()
        if not init_api_url():
            logger.debug("Init api url error")
            return False
        screen_type_init()
        call_api()
        if not check_api_result():
            logger.debug("Check api error")
            return False
        if not prepare_info():
            logger.debug("Prepare info error")
            return False
        if not prepare_img_link():
            logger.debug("Prepare img link error")
            return False
        prepare_img_id()
        download_fin_img()
        check_download_result()
        send_img_result()
    except Exception as e:
        error_info = f'SiteType: `{site_type}`\n'
        error_info += f'ImageID: `{img_id}`\n'
        error_info += f'DownloadURL: `{download_url}`'
        logger.error(error_info)
        remove_temp_file()
