from tgfunc import *

start_text = "Maribel 只是一个微不足道的图片机器人，欢迎指教\n" \
             "`Maribel is just a negligible pic bot, suggestions are greatly appreciated.`"

def start(update: dict) -> bool:
    try:
        if u'group' in update['message']['chat']['type']:
            return False
        if update['message'].get('text','') == u'/start':
            send_message(update, True, start_text)
            return True
        else:
            return False
    except:
        return False