#maribel-telegram—function
import json
import requests
import logging
from . import config

session = requests.Session()
logger = logging.getLogger('Maribel')

def send_typing(update: dict, type=None):
    status = "typing"
    if type:
        status = type
    session.get(
        config.api_url + 'sendChatAction',
        params=dict(chat_id=update['message']['chat']['id'], action=status))


def send_message(update: dict, is_markdown: bool, echo_message: str):
    send_typing(update)
    if is_markdown:
        r = session.get(
            config.api_url + 'sendMessage',
            params=dict(chat_id=update['message']['chat']['id'],
                        reply_to_message_id=update['message']['message_id'],
                        parse_mode='Markdown', text=echo_message))
    else:
        r = session.get(
            config.api_url + 'sendMessage',
            params=dict(chat_id=update['message']['chat']['id'],
                        reply_to_message_id=update['message']['message_id'],
                        text=echo_message))
    return json.loads(r.text)


def post_message(update: dict, parse_mode: int, echo_message: str, disable_preview='true'):
    send_typing(update)
    parse_set = ['','Markdown','HTML']
    data = {
        'chat_id': update['message']['chat']['id'],
        'reply_to_message_id': update['message']['message_id'],
        'parse_mode': parse_set[parse_mode],
        'text': echo_message,
        'disable_web_page_preview': disable_preview
    }
    session.post(
        config.api_url + 'sendMessage',
        data
    )


def send_sticker(update: dict, sticker_id: str):
    session.get(
        config.api_url + 'sendSticker',
        params=dict(chat_id=update['message']['chat']['id'],
                    reply_to_message_id=update['message']['message_id'],
                    sticker=sticker_id))


def send_photo_in_url(update: dict, caption: str, keyboard_map: dict, photo_url):
    return session.post(
                config.api_url + 'sendPhoto',
                data = {
                    'chat_id': update['message']['chat']['id'],
                    'caption': caption,
                    'photo': photo_url,
                    'reply_markup': json.dumps(keyboard_map)
                }
            )


def send_photo(update: dict, caption: str, keyboard_map: dict, photo_handle):
    return session.post(
                config.api_url + 'sendPhoto',
                data = {
                    'chat_id': update['message']['chat']['id'],
                    'caption': caption,
                    'reply_markup': json.dumps(keyboard_map)
                },
                files = {
                    'photo': ('sent.jpg',photo_handle,'image/jpeg')
                }
            )


def inline_raw_button(update: dict, hint_text: str, keyboard_map: dict):
    send_typing(update)
    session.post(
        config.api_url + 'sendMessage',
        data={
            'chat_id': update['message']['chat']['id'],
            'text': hint_text,
            'reply_markup': json.dumps(keyboard_map)
        }
    )


def edit_inline_message(update: dict, hint_text: str, keyboard_map: dict):
    session.post(
        config.api_url + 'editMessageText',
        data={
            'chat_id': update['message']['chat']['id'],
            'message_id': update['message']['message_id'],
            'text': hint_text,
            'reply_markup': json.dumps(keyboard_map)
        }
    )


def answer_callback_query(update: dict):
    session.post(
        config.api_url + 'answerCallbackQuery',
        data={
            'callback_query_id': update['callback_query']['id']
        }
    )


def get_chat_info(chat_id: str) -> dict:
    result = session.get(
        config.api_url + 'getChat',
        params=dict(chat_id=chat_id))
    return json.loads(result.content.decode(encoding='UTF-8'))


def get_chat_member(cid, uid, dump=False) -> bool:
    r = json.loads(session.get(
        config.api_url + 'getChatMember',
        params=dict(chat_id=cid,user_id=uid)
        ).text
    )
    if dump:
        return json.dumps(r, indent=4, ensure_ascii=False)
    return r


def check_if_administrator_or_master(update: dict) -> bool:
    if config.admin_id == update['message']['from']['id']:
        return True
    check_json = get_chat_member(update['message']['chat']['id'],update['message']['from']['id'])
    try:
        if u'administrator' in check_json['result']['status'] or u'creator' in check_json['result']['status']:
            return True
        else:
            return False
    except KeyError:
        return False


