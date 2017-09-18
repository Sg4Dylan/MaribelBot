
import os
import uuid
import configparser
from bs4 import BeautifulSoup
from tgfunc import *

headers = {
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
    'DNT': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2873.0 Safari/537.36',
}
hd_mode_config = "./db/hdmode.ini"

def theanimegallery(update: dict) -> bool:
    
    def hd_status():
        config_ins = configparser.ConfigParser()
        config_ins.read(hd_mode_config)
        return config_ins.getboolean('HD-Mode', str(update['message']['chat']['id']), fallback=False)
    
    try:
        if u'http' in update['message']['text']:
            return False
        elif u'/theanimegallery' in update['message']['text']:
            print("img engine one start...")
            # 抓取信息
            source_url = "http://www.theanimegallery.com/gallery/image:random"
            info_fetch_result = requests.get(source_url, headers=headers)
            soup = BeautifulSoup(info_fetch_result.content.decode("utf-8"), "html.parser")
            img_sample_soup = BeautifulSoup(str(soup.select("[class~=block]")[0]), "html.parser")
            img_sample_url = "http://www.theanimegallery.com" + img_sample_soup.img['src']
            img_file_soup = BeautifulSoup(str(soup.select("[class~=main]")[0]), "html.parser")
            img_file_url = "http://www.theanimegallery.com" + img_file_soup.a['href']
            # HD-Mode
            if hd_status():
                img_sample_url = img_file_url
            print(img_sample_url, img_file_url)
            # 下载图片
            download_img_name = str(uuid.uuid4()) + '.jpg'
            curl_command = "curl -o " + download_img_name + \
                           " -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
                           "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2906.0 Safari/537.36' "
            final_command = curl_command + img_sample_url
            os.system(final_command)
            # 发送图片 + 发送按钮
            button_dict = {
                'inline_keyboard': [[{
                    'text': "查看原图",
                    'url': img_file_url,
                },{
                    'text': "再来一张",
                    'callback_data': update['message']['text']
                }]],
            }
            print("Ready to send photo")
            send_typing(update, "upload_photo")
            send_photo(
                update=update,
                caption="File size: " + \
                str(round(os.path.getsize(download_img_name) / 1024, 2)) + "KiB",
                keyboard_map=button_dict,
                photo_handle=open(download_img_name, 'rb')
            )
            # 清除图片临时文件
            os.remove(download_img_name)
            return True
        else:
            return False
    except:
        return False