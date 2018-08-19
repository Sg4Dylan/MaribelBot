from multiprocessing import Process
from .theanimegallery import theanimegallery
from .five_in_one import five_in_one
from .tags_recommand import tags_cloud
from .null import null
from tgfunc import *

def callback_process(update: dict) -> bool:
    try:
        if 'callback_query' in update:
            # 取出回调 data 为 CallbackQuery 增加一般 Message 固有的的 text 段
            update['callback_query']['message']['text'] = update['callback_query']['data']
            update['callback_query']['callback_query'] = True
            logger.debug(f"New callback query: {update['callback_query']['message'].get('text','')}")
            # 异步消息需先回应
            answer_callback_query(update)
            # 完整的 伪-Message
            callback_update = update['callback_query']
            # 批量产生进程调用函数
            jobs = []
            for function_name in [theanimegallery, five_in_one, tags_cloud, null]:
                global_job = Process(target=function_name, args=(callback_update,))
                jobs.append(global_job)
                global_job.start()
            jobs[-1].terminate()
    except OSError:
        logger.critical("CallbackMemoryError")
    except Exception as e:
        logger.error(f'Callback process ERROR: {e}')
    return False
