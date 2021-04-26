# -*- coding: utf-8 -*-

# import for Tornado WebHook
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.gen
from tornado.options import define, options, parse_command_line
# multi-thread async
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
# multi-processing
from multiprocessing import Pool
# application lib
import os
import json
import logging
import coloredlogs
from pathlib import Path
# bot setting
import config
# bot library
import tgfunc

logger = logging.getLogger('Maribel')
logger.propagate = False
coloredlogs.install(level='ERROR',
                    fmt='%(asctime)s,%(msecs)03d %(name)s[%(process)d] %(levelname)s %(message)s',
                    logger=logger)

# Tornado define
logging.getLogger('tornado.access').disabled = True
define("port", default=8021, help="run on the given port", type=int)
logger.critical('Maribel WebHook API Server started.')


# Bot Web Hook event engine
class FinalEventHandler(tornado.web.RequestHandler):
    # Tornado Threadpool
    executor = ThreadPoolExecutor(5)
    # Plugin Multiprocessing Pool
    mpool = Pool(processes=5)

    @tornado.gen.coroutine
    def post(self):
        # logger.debug(self.request.body.decode(encoding='UTF-8'))
        output_string = yield self.execute_job()
        # detect type
        if not isinstance(output_string, str):
            output_string = 'ERROR'
        self.write(output_string)
        self.finish()

    @run_on_executor
    def execute_job(self):
        try:
            return_string = "OK"
            # print(self.request.body)
            update = json.loads(self.request.body.decode(encoding='UTF-8'))
            # Black List
            chat_id = 0
            if 'message' in update:
                if 'chat' in update['message']:
                    chat_id = update['message']['chat'].get('id',0)
            # Trigger by all type message
            for function_name in config.global_trigger:
                self.mpool.apply_async(function_name, args=(update,))
            # Trigger by message from group only
            try:
                if (u'group' in update['message']['chat']['type'] and
                        config.bot_id in update['message']['text']) or \
                        u'private' in update['message']['chat']['type']:
                    for function_name in config.group_trigger:
                        self.mpool.apply_async(function_name, args=(update,))
            except:
                pass
            # Trigger by callback
            if 'callback_query' in update:
                update['callback_query']['message']['text'] = update['callback_query']['data']
                update['callback_query']['callback_query'] = True
                logger.debug(f"New callback query: {update['callback_query']['message'].get('text','')}")
                tgfunc.answer_callback_query(update)
                jobs = []
                for function_name in config.callback_trigger:
                    self.mpool.apply_async(function_name, args=(update['callback_query'],))
            return return_string
        except UnicodeDecodeError:
            logger.critical("Unicode Decode Error")
        except OSError:
            logger.critical("EntryPointMemoryError")


if __name__ == "__main__":
    # Remove Temp File
    for p in Path(".").glob("*.jpg"):
        p.unlink()
    # RUN Tornado
    parse_command_line()
    route_handlers = [
        (r"/", FinalEventHandler)
    ]
    app = tornado.web.Application(handlers=route_handlers)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port, address="127.0.0.1")
    tornado.ioloop.IOLoop.instance().start()
