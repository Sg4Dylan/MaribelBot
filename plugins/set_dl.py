from PIL import Image
from io import BytesIO
import shutil
import os
import threading
import time
import zipfile
from tgfunc import *

def set_dl(update: dict):
    
    def download_unit(set_title,file_id):
        # 下载原图
        req_body = get_file_by_path(get_file_path(file_id))
        # 导入文件
        sticker_im = Image.open(BytesIO(req_body)).convert('RGBA')
        # 创建临时文件夹
        save_path = f'./{set_name}/{file_id}.png'
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        # 转换保存
        sticker_im.save(save_path, 'PNG')
    
    def sent_pack(set_name):
        zip_path = f'./sticker_temp/{set_name}'
        send_document(
            update, 
            "", 
            open(f'{zip_path}.zip', mode='rb').read(),
            f"{set_name}.zip",
            'application/zip')
    
    def cache_detect(set_name,set_list):
        zip_path = f'./sticker_temp/{set_name}.zip'
        if not os.path.isfile(zip_path):
            return False
        exists_zip_list = []
        with zipfile.ZipFile(zip_path, 'r') as set_zip:
            exists_zip_list = set_zip.namelist()
        for item in set_list:
            item_name = f"{item['file_id']}.png"
            if not item_name in exists_zip_list:
                return False
        return True
    
    def converter_unit(set_name):
        tip_text = "`菜鸡服务器已收到请求，正在下载转换中...`\n" \
                  "`The server has received the request and is process the task...`"
        status_msg = send_message(update, True, tip_text)
        # 解析图集
        set_info = get_sticker_set(set_name)
        if not set_info.get('ok', False):
            err_text = "`未找到关联的 sticker set`\n" \
                       "`The associated sticker set was not found`"
            edit_message_text(status_msg,err_text,1)
            return
        set_title = set_info['result'].get('title','')
        set_list = set_info['result']['stickers']
        tip_text = "`Sticker set 解析完毕！`\n" \
                   "`Sticker set has parsed!`"
        edit_message_text(status_msg,tip_text,1)
        # 检查缓存
        dl_path = f'./{set_name}'
        zip_path = f'./sticker_temp/{set_name}'
        if cache_detect(set_name,set_list):
            tip_text = "`侦测到已完成的打包任务！准备发送中...`\n" \
                       "`Detected a completed task! Ready to send...`"
            edit_message_text(status_msg,tip_text,1)
            sent_pack(set_name)
            tip_text = "尽情享用~\n" \
                       "`Enjoy it`"
            edit_message_text(status_msg,tip_text,1)
            return
        # 下载
        sticker_count = len(set_list)
        done_count = 0
        tip_text = "`准备追加任务至下载队列...`\n" \
                   "`Preparing to add the task to the download queue`"
        edit_message_text(status_msg,tip_text,1)
        # 准备下载线程
        dl_threads = []
        for sticker in set_list:
            task = threading.Thread(target=download_unit,args=(set_title,sticker['file_id'],))
            task.setDaemon(False)
            dl_threads.append(task)
            done_count += 1
            tip_text = "下载任务追加中 `Appending download task`\n" \
                       f"({done_count}/{sticker_count})..."
            amsg = threading.Thread(
                target=edit_message_text, 
                args=(status_msg,tip_text,1,))
            amsg.start()
            time.sleep(0.1)
        # 启动下载线程
        for task in dl_threads:
            task.start()
        # 等待任务完成
        tip_text = "`下载任务执行中...`\n" \
                   "`Executing download task...`"
        edit_message_text(status_msg,tip_text,1)
        for task in dl_threads:
            task.join()
        tip_text = "`下载完成，开始打包...`\n" \
                   "`Download completed, start packing...`"
        edit_message_text(status_msg,tip_text,1)
        # 打包
        shutil.make_archive(zip_path, 'zip', dl_path)
        shutil.rmtree(set_name)
        # 发送
        tip_text = "`打包文件传送中...`\n" \
                   "`Sending packed file...`"
        edit_message_text(status_msg,tip_text,1)
        sent_pack(set_name)
        tip_text = "尽情享用~\n" \
                   "`Enjoy it`"
        edit_message_text(status_msg,tip_text,1)
    
    if 'reply_to_message' in update['message']:
        # 检查类型
        if not 'sticker' in update['message']['reply_to_message']:
            return
        # 检查输出参数
        if update['message'].get('text', "").upper().startswith("/PKSDL"):
            set_name = update['message']['reply_to_message']['sticker'].get('set_name','')
            logger.info(f'Send set name: {set_name}')
            converter_unit(set_name)