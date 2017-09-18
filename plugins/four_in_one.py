
import os
import json
import uuid
import random
import requests
import configparser
import xml.etree.cElementTree as ET
from tgfunc import *

headers = {
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
    'DNT': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2873.0 Safari/537.36',
}

def four_in_one(update: dict) -> bool:
    
    # 站点类型
    site_type = 0
    # 用户输入标签
    tag_list = []
    # API URL
    source_url = ""
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
    # 图片 ID
    img_id = ""
    # 图片文件名
    download_img_name = ""
    # 下载失败标记
    download_fail_flag = False
    # 图片尺寸
    img_size = ""
    # 安全 roll
    check_result = True
    roll_count = 128
    config_file_path = "./db/safemode.ini"
    # HD Mode
    hd_mode_config = "./db/hdmode.ini"
    
    def init_site_type():
        nonlocal site_type
        if u'http' in update['message']['text']:
            return False
        elif u'/yandere' in update['message']['text']:
            site_type = 0
        elif u'/konachan' in update['message']['text']:
            site_type = 1
        elif u'/danbooru' in update['message']['text']:
            site_type = 2
        elif u'/3dbooru' in update['message']['text']:
            site_type = 3
        elif u'/gelbooru' in update['message']['text']:
            site_type = 4
        else:
            return False
        return True
    
    def init_tag():
        nonlocal tag_list
        # 分离参数
        try:
            tag_list.append(update['message']['text'].split(' ', 1)[1])
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
    
    def call_api():
        nonlocal site_type, source_url, result_json, xml_to_list
        try:
            if site_type != 4:
                result_json = json.loads(requests.get(source_url, headers=headers).content.decode(encoding='UTF-8'))
            else:
                xml_fetch_result = requests.get(source_url, headers=headers).content.decode(encoding='UTF-8')
                xml_fetch_root = ET.fromstring(xml_fetch_result)
                for child in xml_fetch_root:
                    xml_to_list.append(child.attrib)
        except Exception as e:
            print(e)
    
    def check_api_result():
        # 探测抓取结果
        nonlocal result_json, xml_to_list, site_type
        if str(result_json) == "[]" and site_type != 4:
            send_message(update, True, "十分抱歉，您查找的_tag_并没有结果")
            send_sticker(update, 'BQADBQADtgEAAnVo_QMW7xR_mxZf8wI')
            return False
        if not xml_to_list and site_type == 4:
            send_message(update, True, "十分抱歉，您查找的_tag_并没有结果")
            send_sticker(update, 'BQADBQADtgEAAnVo_QMW7xR_mxZf8wI')
            return False
        return True
    
    def prepare_random_id():
        # 准备随机数
        nonlocal site_type, random_img_id, xml_to_list, result_json
        if site_type == 4:
            random_img_id = random.randint(0, len(xml_to_list) - 1)
        else:
            random_img_id = random.randint(0, len(result_json) - 1)
        safe_module_filter()
    
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
    
    def safe_module_filter():
        
        nonlocal roll_count, config_file_path, check_result
        
        def safe_status():
            config_ins = configparser.ConfigParser()
            config_ins.read(config_file_path)
            return config_ins.getboolean('SafeModule', str(update['message']['chat']['id']), fallback=False)
        
        if not safe_status():
            return
        print("[SafeModule] SFW enable.")
        result_k = ""
        if site_type == 4:
            result_k = xml_to_list[random_img_id]["rating"]
        else:
            result_k = result_json[random_img_id]["rating"]
        if result_k != "s" and roll_count > 0:
            roll_count -= 1
            if roll_count == 0:
                send_message(update, True, "出于当前安全设定考虑，您请求内容已被阻止")
                check_result = False
            else:
                prepare_random_id()
    
    def prepare_img_link():
        nonlocal site_type, img_sample_url, img_file_url, result_json, xml_to_list, random_img_id, check_result
        print("[SafeModule] start safe check.")
        prepare_random_id()
        if not check_result:
            return False
        
        def hd_status():
            config_ins = configparser.ConfigParser()
            config_ins.read(hd_mode_config)
            return config_ins.getboolean('HD-Mode', str(update['message']['chat']['id']), fallback=False)
        
        # 设定图片链接
        if site_type == 1:
            img_sample_url = "https:" + result_json[random_img_id]["sample_url"]
            img_file_url = "https:" + result_json[random_img_id]["file_url"]
        elif site_type == 2:
            img_sample_url = "https://danbooru.donmai.us" + result_json[random_img_id]["file_url"]
            img_file_url = "https://danbooru.donmai.us" + result_json[random_img_id]["large_file_url"]
        elif site_type == 3:
            if result_json[random_img_id]["source"] != "":
                img_sample_url = result_json[random_img_id]["source"]
                img_file_url = result_json[random_img_id]["source"]
            else:
                img_sample_url = result_json[random_img_id]["sample_url"]
                img_file_url = "http://behoimi.org/post/show/" + str(result_json[random_img_id]["id"])
        elif site_type == 4:
            img_sample_url = "https:" + xml_to_list[random_img_id]['sample_url']
            img_file_url = "https:" + xml_to_list[random_img_id]['file_url']
        else:
            img_sample_url = result_json[random_img_id]["sample_url"]
            img_file_url = result_json[random_img_id]["file_url"]
        
        if hd_status():
            print("[HD-Mode] HD mode enable.")
            img_sample_url = img_file_url
        
        return True
        
    def prepare_img_id():
        nonlocal site_type, img_id, xml_to_list, result_json, random_img_id
        if site_type == 4:
            img_id = str(xml_to_list[random_img_id]['id'])
        else:
            img_id = str(result_json[random_img_id]["id"])
        
    def download_fin_img():
        nonlocal download_img_name, result_json, random_img_id, img_sample_url
        # 下载图片
        download_img_name = str(uuid.uuid4()) + '.jpg'
        curl_command = "curl -o " + download_img_name + \
                       " -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
                       "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2906.0 Safari/537.36' "
        if site_type == 3:
            curl_command = curl_command + "--referer " + "http://behoimi.org/post/show/" + \
                           str(result_json[random_img_id]["id"]) + " "
        final_command = curl_command + img_sample_url
        # DEBUG
        # print(final_command)
        os.system(final_command)
        
    def check_download_result():
        nonlocal img_size, download_img_name, download_img_name, random_img_id, caption_text
        download_img_size = os.path.getsize(download_img_name)
        if download_img_size == 44020:
            download_fail_flag = True
            caption_text = 'Fail to download image\n' + caption_text
        if site_type == 4:
            img_size = str(round(download_img_size / 1024, 2))
        else:
            img_size = str(round(result_json[random_img_id]["file_size"] / 1024, 2))
        
    def send_img_result():
        nonlocal caption_text, img_id, download_img_name, img_size, img_file_url
        # 发送图片 + 发送按钮
        print("Ready to send photo")
        button_dict = {
            'inline_keyboard': [[{
                'text': "查看原图",
                'url': img_file_url,
            },{
                'text': "再来一张",
                'callback_data': update['message']['text']
            }]],
        }
        if not download_fail_flag:
            send_typing(update, "upload_photo")
            send_photo(
                update=update,
                caption=caption_text + img_id + " File size: " + img_size + "KiB",
                keyboard_map=button_dict,
                photo_handle=open(download_img_name, 'rb')
            )
        # 清除图片临时文件
        os.remove(download_img_name)
        return True
    
    try:
        if not init_site_type():
            return False
        init_tag()
        if not init_api_url():
            print("Init api url error")
            return False
        call_api()
        if not check_api_result():
            print("Check api error")
            return False
        if not prepare_info():
            print("Prepare info error")
            return False
        if not prepare_img_link():
            print("Prepare img link error")
            return False
        prepare_img_id()
        download_fin_img()
        check_download_result()
        send_img_result()
    except Exception as e:
        print("Global Error: %s" % e)
    
