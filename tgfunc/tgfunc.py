#maribel-telegram—function
import json
import requests
from . import config


def send_typing(update: dict, type=None):
    status = "typing"
    if type:
        status = type
    requests.get(
        config.api_url + 'sendChatAction',
        params=dict(chat_id=update['message']['chat']['id'], action=status))


def send_message(update: dict, is_markdown: bool, echo_message: str):
    send_typing(update)
    if is_markdown:
        requests.get(
            config.api_url + 'sendMessage',
            params=dict(chat_id=update['message']['chat']['id'],
                        reply_to_message_id=update['message']['message_id'],
                        parse_mode='Markdown', text=echo_message))
    else:
        requests.get(
            config.api_url + 'sendMessage',
            params=dict(chat_id=update['message']['chat']['id'],
                        reply_to_message_id=update['message']['message_id'],
                        text=echo_message))


def post_message(update: dict, is_html: bool, echo_message: str):
    send_typing(update)
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
        config.api_url + 'sendMessage',
        data
    )


def send_sticker(update: dict, sticker_id: str):
    requests.get(
        config.api_url + 'sendSticker',
        params=dict(chat_id=update['message']['chat']['id'],
                    reply_to_message_id=update['message']['message_id'],
                    sticker=sticker_id))


def send_photo(update: dict, caption: str, keyboard_map: dict, photo_handle):
    requests.post(
        config.api_url + 'sendPhoto',
        data = {
            'chat_id': update['message']['chat']['id'],
            'caption': caption,
            'reply_markup': json.dumps(keyboard_map)
        },
        files = {
            'photo': ('send.jpg',photo_handle,'image/jpeg')
        }
    )


def inline_raw_button(update: dict, hint_text: str, keyboard_map: dict):
    send_typing(update)
    requests.post(
        config.api_url + 'sendMessage',
        data={
            'chat_id': update['message']['chat']['id'],
            'text': hint_text,
            'reply_markup': json.dumps(keyboard_map)
        }
    )


def edit_inline_message(update: dict, hint_text: str, keyboard_map: dict):
    requests.post(
        config.api_url + 'editMessageText',
        data={
            'chat_id': update['message']['chat']['id'],
            'message_id': update['message']['message_id'],
            'text': hint_text,
            'reply_markup': json.dumps(keyboard_map)
        }
    )


def answer_callback_query(update: dict):
    requests.post(
        config.api_url + 'answerCallbackQuery',
        data={
            'callback_query_id': update['callback_query']['id']
        }
    )


def get_chat_info(chat_id: str) -> dict:
    result = requests.get(
        config.api_url + 'getChat',
        params=dict(chat_id=chat_id))
    return json.loads(result.content.decode(encoding='UTF-8'))


def check_if_administrator_or_master(update: dict) -> bool:
    if config.admin_id == update['message']['from']['id']:
        return True
    check_request_body = requests.get(
        config.api_url + 'getChatMember',
        params=dict(chat_id=update['message']['chat']['id'],
                    user_id=update['message']['from']['id'])).content
    check_json = json.loads(check_request_body.decode(encoding='UTF-8'))
    try:
        if u'administrator' in check_json['result']['status'] or u'creator' in check_json['result']['status']:
            return True
        else:
            return False
    except KeyError:
        return False