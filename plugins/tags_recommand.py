import json
import random
import requests
from tgfunc import *

headers = {
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
    'DNT': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2873.0 Safari/537.36',
}
site_type_hint = {
    "type_yandere": "https://yande.re/tag.json?order=count&limit=200",
    "type_konachan": "https://konachan.com/tag.json?order=count&limit=200",
    "type_danbooru": "https://danbooru.donmai.us/tags.json?order=count&limit=200",
    "type_3dbooru": "http://behoimi.org/tag/index.json?order=count&limit=200"
}
site_commands = {
    "type_yandere": "/yandere@MaribelBot ",
    "type_konachan": "/konachan@MaribelBot ",
    "type_danbooru": "/danbooru@MaribelBot ",
    "type_3dbooru": "/3dbooru@MaribelBot "
}

def tags_cloud(update: dict) -> bool:

    # 站点类型
    site_type = ""
    # 站点API
    site_api = ""
    # 标签集
    tags_list = []

    # 第二级选单
    def init_site_type():
        nonlocal site_type, site_api
        if u'http' in update['message']['text']:
            return False
        for item in site_type_hint:
            if update['message'].get('text', '').startswith(item):
                site_type, site_api = item, site_type_hint[item]
                return True
        return False

    # 获取 tag 列表
    def get_api_content():
        nonlocal tags_list
        tags_raw = requests.get(site_api, headers=headers).content.decode("UTF-8")
        tags_dict = json.loads(tags_raw)
        for item in tags_dict:
            tags_list.append(item['name'])
        # 随机化
        random.shuffle(tags_list)

    # 第一级选单
    def send_keyboard_select_source():
        button_dict = {
            'inline_keyboard': [[{
                'text': "Yandere",
                'callback_data': "type_yandere"
            },{
                'text': "Konachan",
                'callback_data': "type_konachan"
            }],[{
                'text': "Dandooru",
                'callback_data': "type_danbooru"
            },{
                'text': "3dbooru",
                'callback_data': "type_3dbooru"
            }]]
        }
        hint_text = "请选择Tag来源："
        if "retake_menu_one" in update['message']['text']:
            edit_inline_message(update, hint_text, button_dict)
        else:
            inline_raw_button(update, hint_text, button_dict)

    # 第二级选单
    def send_keyboard_select_tag():
        button_dict = {'inline_keyboard': []}
        print(type(tags_list))
        for i in range(4):
            line_list = []
            for j in range(4):
                element_dict = {}
                element_dict['text'] = tags_list[i*4+j]
                element_dict['callback_data'] = site_commands[site_type] + tags_list[i*4+j]
                if i==3 and j== 3:
                    element_dict['text'] = "换一波💦"
                    element_dict['callback_data'] = site_type
                if i==3 and j== 0:
                    element_dict['text'] = "🔙返回"
                    element_dict['callback_data'] = "/tagcloud#retake_menu_one"
                line_list.append(element_dict)
            button_dict['inline_keyboard'].append(line_list)
        hint_text = "请点击你需要获取的标签："
        edit_inline_message(update, hint_text, button_dict)

    try:
        if update['message'].get('text', '').startswith("/tagcloud"):
            send_keyboard_select_source()
        if not init_site_type():
            return False
        get_api_content()
        send_keyboard_select_tag()
    except Exception as e:
        print("Global Error: %s" % e)

