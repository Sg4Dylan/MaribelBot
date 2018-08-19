import os
import configparser
from tgfunc import *

def hdmode(update: dict) -> bool:

    config_file_path = "./db/hdmode.ini"
    
    def auto_generate_config():
        config_ins = configparser.ConfigParser()
        config_ins.read(config_file_path)
        if not os.path.exists(config_file_path):
            config_ins.add_section('HD-Mode')
            config_ins['HD-Mode']['using'] = "True"
            with open(config_file_path, 'w') as configfile:
                config_ins.write(configfile)
            logger.debug("[HD-Mode] Auto generate config complished.")
    
    def auto_add_chat_id():
        config_ins = configparser.ConfigParser()
        config_ins.read(config_file_path)
        result = config_ins.get('HD-Mode', str(update['message']['chat']['id']), fallback="NotExist")
        if result == "NotExist":
            config_ins['HD-Mode'][str(update['message']['chat']['id'])] = "False"
            with open(config_file_path, 'w') as configfile:
                config_ins.write(configfile)
            logger.debug("[HD-Mode] Auto add chat id complished.")
    
    def set_config(option):
        config_ins = configparser.ConfigParser()
        config_ins.read(config_file_path)
        config_ins['HD-Mode'][str(update['message']['chat']['id'])] = option
        with open(config_file_path, 'w') as configfile:
            config_ins.write(configfile)
        result_msg = "开始使用原图显示" if option=="True" else "开始使用缩略图显示"
        send_message(update, False, result_msg)
    
    def show_status():
        config_ins = configparser.ConfigParser()
        config_ins.read(config_file_path)
        result = config_ins.getboolean('HD-Mode', str(update['message']['chat']['id']), fallback=False)
        status_result = "当前使用原图显示" if result else "当前使用缩略图显示"
        status_result += "\n当前模式可能会降低图片加载速度并增加移动网络流量消耗！" if result else ""
        status_result += "\n群组管理员可以使用命令 `/hdmode [on/off]` 切换预览图设定."
        send_message(update, True, status_result)
    
    def check_user():
        if 'group' in update['message']['chat']['type']:
            return check_if_administrator_or_master(update)
        else:
            return True
    
    def change_switch():
        msg_list = update['message'].get('text', '').split(' ', 1)
        if len(msg_list) == 2:
            if not check_user():
                send_message(update, True, "当前操作需要您具备群组管理权限")
            if msg_list[1].upper() == "ON":
                set_config("True")
            elif msg_list[1].upper() == "OFF":
                set_config("False")
            else:
                pass
        if len(msg_list) == 1:
            show_status()
    
    try:
        if not 'message' in update:
            return False
        if not 'chat' in update['message']:
            return False
        auto_generate_config()
        auto_add_chat_id()
        if update['message'].get('text', '').startswith('/hdmode'):
            change_switch()
    except Exception as e:
       logger.error(f'Plugin HD-Mode ERROR: {e}')
       return False
    return True