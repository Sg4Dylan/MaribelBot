# -*- coding: utf-8 -*-

import requests
import json
import os
import random
from multiprocessing import Process
# import for Tornado WebHook
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.gen
from tornado.options import define, options, parse_command_line
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
# import for python-telegram-bot API
import telegram

# set your token
bot_token = ''
bot = telegram.Bot(token=bot_token)
# Tornado define
define("port", default=8021, help="run on the given port", type=int)

url = 'https://api.telegram.org/bot%s/' % bot_token


def maribel_send_typing(update: dict):
    requests.get(
        url + 'sendChatAction',
        params=dict(chat_id=update['message']['chat']['id'], action='typing'))


def maribel_send_message(update: dict, is_markdown: bool, echo_message: str):
    maribel_send_typing(update)
    if is_markdown:
        requests.get(
            url + 'sendMessage',
            params=dict(chat_id=update['message']['chat']['id'],
                        reply_to_message_id=update['message']['message_id'],
                        parse_mode='Markdown', text=echo_message))
    else:
        requests.get(
            url + 'sendMessage',
            params=dict(chat_id=update['message']['chat']['id'],
                        reply_to_message_id=update['message']['message_id'],
                        text=echo_message))


def maribel_post_message(update: dict, is_html: bool, echo_message: str):
    maribel_send_typing(update)
    if is_html:
        data = {
            'chat_id': update['message']['chat']['id'],
            'reply_to_message_id': update['message']['message_id'],
            'parse_mode': 'HTML',
            'text': echo_message,
        }
    else:
        data = {
            'chat_id': update['message']['chat']['id'],
            'reply_to_message_id': update['message']['message_id'],
            'text': echo_message,
        }
    requests.post(
        url + 'sendMessage',
        data
    ).json()


def maribel_send_sticker(update: dict, sticker_id: str):
    requests.get(
        url + 'sendSticker',
        params=dict(chat_id=update['message']['chat']['id'],
                    reply_to_message_id=update['message']['message_id'],
                    sticker=sticker_id))


def maribel_inline_url_button(update: dict, hint_text: str, button_text: str, url_link: str):
    maribel_send_typing(update)
    button_json_dict = {
        'inline_keyboard': [[{
            'text': button_text,
            'url': url_link
        }]],
    }
    requests.post(
        url + 'sendMessage',
        data={
            'chat_id': update['message']['chat']['id'],
            'reply_to_message_id': update['message']['message_id'],
            'text': hint_text,
            'reply_markup': json.dumps(button_json_dict)
        }
    ).json()


def maribel_picture(update: dict) -> bool:
    try:
        is_yandere = 0
        if u'http' in update['message']['text']:
            return False
        elif u'/yandere' in update['message']['text']:
            pass
        elif u'/konachan' in update['message']['text']:
            is_yandere = 1
        elif u'/danbooru' in update['message']['text']:
            is_yandere = 2
        elif u'/3dbooru' in update['message']['text']:
            is_yandere = 3
        else:
            return False
        print("img engine start...")
        tag_list = []
        try:
            tag_list.append(update['message']['text'].split(' ', 1)[1])
        except IndexError:
            tag_list.append(' ')
        random_page_id = 1
        if tag_list[0] == " ":
            random_page_id = str(random.randint(1, 10))
            if is_yandere == 3:
                random_page_id = str(random.randint(1, 1000))
        if is_yandere == 0:
            source_url = "https://yande.re/post.json?limit=100&page=%s&tags=%s" % (random_page_id,tag_list[0])
        elif is_yandere == 1:
            source_url = "https://konachan.com/post.json?limit=100&page=%s&tags=%s" % (random_page_id,tag_list[0])
        elif is_yandere == 2:
            source_url = "https://danbooru.donmai.us/posts.json?limit=100&page=%s&tags=%s" % (random_page_id,tag_list[0])
        else:
            source_url = "http://behoimi.org/post/index.json?limit=100&page=%s&tags=%s" % (random_page_id,tag_list[0])
        headers = {
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
            'DNT': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2873.0 Safari/537.36',
        }
        try:
            result_json = json.loads(requests.get(source_url, headers=headers).content.decode(encoding='UTF-8'))
        except Exception as e:
            print(e)
        if str(result_json) == "[]":
            maribel_send_message(update, True, "十分抱歉，您查找的_tag_并没有结果")
            maribel_send_sticker(update, 'BQADBQADtgEAAnVo_QMW7xR_mxZf8wI')
            return True
        random_img_id = random.randint(0, len(result_json)-1)
        if is_yandere == 0:
            caption_text = 'Yandere ID: '
        elif is_yandere == 1:
            caption_text = 'Konachan ID: '
        elif is_yandere == 2:
            caption_text = 'Danbooru ID: '
        else:
            caption_text = '3dbooru ID: '
        if is_yandere == 2:
            img_sample_url = "https://danbooru.donmai.us" + result_json[random_img_id]["file_url"]
            img_file_url = "https://danbooru.donmai.us" + result_json[random_img_id]["large_file_url"]
        elif is_yandere == 3:
            if result_json[random_img_id]["source"] != "":
                img_sample_url = result_json[random_img_id]["source"]
                img_file_url = result_json[random_img_id]["source"]
            else:
                img_sample_url = result_json[random_img_id]["sample_url"]
                img_file_url = "http://behoimi.org/post/show/" + str(result_json[random_img_id]["id"])
        else:
            img_sample_url = result_json[random_img_id]["sample_url"]
            img_file_url = result_json[random_img_id]["file_url"]
        download_img_name = str(result_json[random_img_id]["id"]) + '.jpg'
        curl_command = "curl -o " + download_img_name + " -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2873.0 Safari/537.36' "
        if is_yandere == 3:
            curl_command = curl_command + "--referer " + "http://behoimi.org/post/show/" + str(result_json[random_img_id]["id"]) + " "
        final_command = curl_command + img_sample_url
        os.system(final_command)
        download_fail_flag = False
        if os.path.getsize(download_img_name) == 44020:
            download_fail_flag = True
            caption_text = 'Fail to download image\n' + caption_text
        if not download_fail_flag:
            maribel_send_typing(update)
            bot.sendPhoto(
                chat_id=update['message']['chat']['id'],
                photo=open(download_img_name, 'rb'),
                reply_to_message_id=int(update['message']['message_id']),
            )
        maribel_inline_url_button(
            update,
            caption_text + 
            str(result_json[random_img_id]["id"]) + " " + "File size: " + 
            str(round(result_json[random_img_id]["file_size"] / 1024, 2)) + "KiB",
            "Click to view source",
            img_file_url
        )
        os.remove(download_img_name)
        return True
    except:
        return False


def maribel_start(update: dict) -> bool:
    try:
        if u'group' in update['message']['chat']['type']:
            return False
        if update['message']['text'] == u'/start':
            maribel_send_message(update, False, "Maribel 只是一个微不足道的图片机器人，欢迎指教")
            return True
        else:
            return False
    except:
        return False


def maribel_help(update: dict) -> bool:
    try:
        if u'/help' in update['message']['text']:
            help_msg = "给 Maribel 的图片搜索加上相应 tag 可以获取该 tag 下的图片哦" \
                       "\n例如：/konachan touhou" \
                       "\n另外，在群聊时使用 Maribel要记得 at Maribel 的 ID 哦"
            maribel_send_message(update, False, help_msg)
            return True
        else:
            return False
    except:
        return False


def maribel_null(update: dict) -> bool:
    if update:
        pass
    return False


# Bot Web Hook event engine
class FinalEventHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(5)

    @tornado.gen.coroutine
    def post(self):
        # print(self.request.body.decode(encoding='UTF-8'))
        output_string = yield self.execute_job()
        self.write(output_string)
        self.finish()

    @run_on_executor
    def execute_job(self):
        return_string = "OK"
        update = json.loads(self.request.body.decode(encoding='UTF-8'))
        jobs = []
        for function_name in [maribel_start, maribel_null]:
            global_job = Process(target=function_name, args=(update,))
            jobs.append(global_job)
            global_job.start()
        try:
            if u'group' in update['message']['chat']['type']:
                print("From: %s ID: %s Receive: %s" %
                      (update['message']['chat']['title'],
                       str(update['message']['chat']['id']),
                       update['message']['text']))
            else:
                print("From: PM ID: %s Receive: %s" %
                      (str(update['message']['chat']['id']),
                       update['message']['text']))
        except:
            pass
        try:
            if (u'group' in update['message']['chat']['type'] and
                    u'@MaribelBot' in update['message']['text']) or \
                    u'private' in update['message']['chat']['type']:
                for function_name in [maribel_help, maribel_picture, maribel_null]:
                    user_job = Process(target=function_name, args=(update,))
                    jobs.append(user_job)
                    user_job.start()
        except:
            pass
        jobs[-1].terminate()
        return return_string


if __name__ == "__main__":
    parse_command_line()
    app = tornado.web.Application(handlers=[(r"/", FinalEventHandler)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port, address="127.0.0.1")
    tornado.ioloop.IOLoop.instance().start()
