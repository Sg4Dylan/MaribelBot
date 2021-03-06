import os
import configparser
import traceback
from tgfunc import *

def safemodule(update: dict) -> bool:

    config_file_path = "./db/safemode.ini"
    
    def auto_generate_config():
        config_ins = configparser.ConfigParser()
        config_ins.read(config_file_path)
        if not os.path.exists(config_file_path):
            config_ins.add_section('SafeModule')
            config_ins['SafeModule']['using'] = "True"
            with open(config_file_path, 'w') as configfile:
                config_ins.write(configfile)
            logger.debug("[SafeModule] Auto generate config complished.")
    
    def auto_add_chat_id():
        config_ins = configparser.ConfigParser()
        config_ins.read(config_file_path)
        result = config_ins.get('SafeModule', str(update['message']['chat']['id']), fallback="NotExist")
        if result == "NotExist":
            config_ins['SafeModule'][str(update['message']['chat']['id'])] = "False"
            with open(config_file_path, 'w') as configfile:
                config_ins.write(configfile)
            logger.debug("[SafeModule] Auto add chat id complished.")
    
    def set_config(option):
        config_ins = configparser.ConfigParser()
        config_ins.read(config_file_path)
        config_ins['SafeModule'][str(update['message']['chat']['id'])] = option
        with open(config_file_path, 'w') as configfile:
            config_ins.write(configfile)
        result_msg = "安全模式: 已启用" if option=="True" else "安全模式: 已停用"
        result_msg += "\n"
        result_msg += "Safe mode: ON [SFW]" if option=="True" else "Safe mode: OFF [NSFW]"
        send_message(update, False, result_msg)
    
    def show_status():
        config_ins = configparser.ConfigParser()
        config_ins.read(config_file_path)
        result = config_ins.getboolean('SafeModule', str(update['message']['chat']['id']), fallback=False)
        status_result = "安全模式: 已启用" if result else "安全模式: 已停用"
        status_result += "\n群组管理员可以使用命令 `/safemode [on/off]` 切换安全设定."
        status_result += "\n注意：本功能不能作用于 TheAnimeGallery，且对于其他来源也不能保障绝对健全\n"
        status_result += "Safe mode: ON `[SFW]`" if result else "Safe mode: OFF `[NSFW]`"
        status_result += "\nGroup admin can use the command `/safemode [on/off]` to switch setting."
        status_result += "\nNotice: This feature does not work on TheAnimeGallery and does not guarantee absolute safety for other sources.\n"
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
                send_message(update, True, "当前操作需要您具备群组管理权限\n`Current operation requires you to have group admin rights`")
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
        if update['message'].get('text', '').startswith('/safemode'):
            change_switch()
    except Exception as e:
       logger.error(f'Plugin Safe-Mode ERROR: {e}')
       error_upload(
            update,
            'Plugin Safe-Mode - ERROR',
            f'{type(e)}',
            'Call /safemode error',
            f'{traceback.format_exc()}'
        )
       return False
    return True