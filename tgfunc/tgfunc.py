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


def get_file_by_path(file_path: str):
    file_url = f'https://api.telegram.org/file/bot{config.bot_token}/{file_path}'
    return session.get(file_url).content


def get_file_path(file_id: str):
    j = json.loads(session.get(
        config.api_url + 'getFile',
        params=dict(file_id=file_id)).text)
    if j['ok']:
        return j['result'].get('file_path','')


def send_document(update:dict, caption_msg: str, doc_file, file_name=None, file_mime=None, reply_id=None):
    reply_to_id = update['message']['message_id']
    if reply_id:
        reply_to_id = reply_id
    send_typing(update, "upload_document")
    return session.post(
        config.api_url + 'sendDocument',
        files=dict(document=(file_name,
                             doc_file,
                             file_mime)),
        data=dict(chat_id=update['message']['chat']['id'],
                  caption=caption_msg,
                  reply_to_message_id=reply_to_id))


def get_sticker_set(set_name: str):
    return json.loads(session.get(
        config.api_url + 'getStickerSet',
        params={'name': set_name}).text)


def edit_message_text(message: dict,
                        new_message: str,
                        parse_mode: int=0, 
                        disable_preview: str='true'):
    data = {
        'chat_id': message['result']['chat']['id'],
        'message_id': message['result']['message_id'],
        'text': new_message,
        'disable_web_page_preview': disable_preview
    }
    if parse_mode == 1:
        data['parse_mode'] = 'Markdown'
    if parse_mode == 2:
        data['parse_mode'] = 'HTML'
    send_typing(update={'message': message['result']})
    return json.loads(session.post(
        config.api_url + 'editMessageText',
        data=data).text)

def chatid_empty_dict(chatid: str):
    prepare_dict = {
        'message': {
            'chat': {
                'id': chatid
            },
            'message_id': ''
        }
    }
    return prepare_dict

def error_upload(update: dict, module_name:str, error_type: str, error_info: str, error_trace:str):
    error_msg = f'Error occurred\n=========\n'
    error_msg += f'Module： `{module_name}`\n'
    error_msg += f'Type： `{error_type}`\n'
    error_msg += f'Info： \n`{error_info}`\n=========\n'
    error_msg += f'Traceback： \n`{error_trace}`\n=========\n'
    error_msg += f'Via： \n`{update}`\n'
    logger.error(error_msg)
    post_message(
        chatid_empty_dict(str(config.admin_id)),
        1,
        error_msg
    )

def fix_duplicate(ini: str):
    raw = open(ini,'rb').read().decode('UTF-8').split('\n')
    new = f'{raw[0]}\n'
    for i in range(1,len(raw)):
        if not raw[i].split('=')[0].strip() in new:
            new += f'{raw[i]}\n'
        else:
            print(f'{raw[i]}')
    with open(ini,'wb') as wp:
        wp.write(new.encode('UTF-8'))










