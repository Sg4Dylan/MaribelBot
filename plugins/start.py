from tgfunc import *

def start(update: dict) -> bool:
    try:
        if 'group' in update['message']['chat']['type']:
            return False
        if update['message'].get('text','') == '/start':
            send_message(update, False, "Maribel 只是一个微不足道的图片机器人，欢迎指教")
            return True
        else:
            return False
    except:
        return False