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
from multiprocessing import Process
# application lib
import json
import logging
import coloredlogs
# bot setting
import config

logger = logging.getLogger('Maribel')
logger.propagate = False
coloredlogs.install(level='DEBUG',
                    fmt='%(asctime)s,%(msecs)03d %(name)s[%(process)d] %(levelname)s %(message)s',
                    logger=logger)

# Tornado define
logging.getLogger('tornado.access').disabled = True
define("port", default=8021, help="run on the given port", type=int)
logger.critical('Maribel WebHook API Server started.')

# Bot Web Hook event engine
class FinalEventHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(5)

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
            update = json.loads(self.request.body.decode(encoding='UTF-8'))
            jobs = []
            # Trigger by all type message
            for function_name in config.global_trigger:
                global_job = Process(target=function_name, args=(update,))
                jobs.append(global_job)
                global_job.start()
            # Trigger by message from group only
            try:
                if (u'group' in update['message']['chat']['type'] and
                        config.bot_id in update['message']['text']) or \
                        u'private' in update['message']['chat']['type']:
                    # 
                    for function_name in config.group_trigger:
                        user_job = Process(target=function_name, args=(update,))
                        jobs.append(user_job)
                        user_job.start()
            except:
                pass
            jobs[-1].terminate()
            return return_string
        except OSError:
            logger.critical("EntryPointMemoryError")


if __name__ == "__main__":
    parse_command_line()
    app = tornado.web.Application(handlers=[(r"/", FinalEventHandler)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port, address="127.0.0.1")
    tornado.ioloop.IOLoop.instance().start()
