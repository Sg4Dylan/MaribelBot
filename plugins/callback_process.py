from multiprocessing import Process
from .theanimegallery import theanimegallery
from .four_in_one import four_in_one
from .tags_recommand import tags_cloud
from .null import null
from tgfunc import *

def callback_process(update: dict) -> bool:
    try:
        if 'callback_query' in update:
            # 取出回调 data 为 CallbackQuery 增加一般 Message 固有的的 text 段
            update['callback_query']['message']['text'] = update['callback_query']['data']
            print("New callback query: ", update['callback_query']['message']['text'])
            # 异步消息需先回应
            answer_callback_query(update)
            # 完整的 伪-Message
            callback_update = update['callback_query']
            # 批量产生进程调用函数
            jobs = []
            for function_name in [theanimegallery, four_in_one, tags_cloud, null]:
                global_job = Process(target=function_name, args=(callback_update,))
                jobs.append(global_job)
                global_job.start()
            jobs[-1].terminate()
    except Exception as e:
        print(e)
    return False
