# -*- coding: utf-8 -*-
__author__ = 'quchunyu@baidu.com'

import logging
import os
import signal
import time
import json

from tornado import ioloop
from tornado import web
from tornado.httpserver import HTTPServer

from framework.named_pipe import NamedPipe

MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 1


class BaseApp(object):

    def __init__(self, port=8899, routings=None, template_path=None, debug=True, gzip=False,  
            login_url=None, cookie_secret=None):  
        if routings is None:
            routings = []
        if template_path is None:
            template_path = []
        if login_url is None:
            login_url='/api/system/login'
        if cookie_secret is None:
            cookie_secret = "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E="

        self.port = port
        self.debug = debug
        self.gzip = gzip
        self.server = None
        self.routings = routings
        self.template_path = template_path
        self.login_url = login_url
        self.cookie_secret = cookie_secret
        self.application = None

    def sig_handler(self, sig, frame):
        """

        :param sig:
        :param frame:
        :return:
        """
        logging.warning('Caught signal: %s', sig)
        ioloop.IOLoop.instance().add_callback(self.shutdown)

    def shutdown(self):
        """

        :return:
        """
        logging.info('Stopping http server')
        self.server.stop()

        logging.info('Will shutdown in %s seconds ...', MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)
        io_loop = ioloop.IOLoop.instance()

        deadline = time.time() + MAX_WAIT_SECONDS_BEFORE_SHUTDOWN

        def stop_loop():
            """

            :return:
            """
            now = time.time()
            if now < deadline:
                io_loop.add_timeout(now + 1, stop_loop)
            else:
                io_loop.stop()
                logging.info('Shutdown')

        stop_loop()

    def start(self):
        """

        :param port:
        :return:
        """
        pid_file = 'var/%d.pid' % self.port

        if self.debug or not os.path.exists(pid_file):
            with open(pid_file, 'w') as f:
                f.write(str(os.getpid()))
               
            try:
                self.initialize()
                self.application = web.Application(
                    handlers=self.routings,
                    template_path=self.template_path,
                    debug=self.debug,
                    gzip=self.gzip,
                    login_url=self.login_url,
                    cookie_secret=self.cookie_secret)

                self.application.status = 0
                self.application.json = json.dumps({})
                # self.application.pipe = NamedPipe(self, '/tmp/_out_execution.pipe', '/tmp/_in_execution.pipe')

                # MaxUpload size, set to 500M
                self.server = HTTPServer(self.application, max_buffer_size=524288000)
                self.server.listen(self.port)

                signal.signal(signal.SIGTERM, self.sig_handler)
                signal.signal(signal.SIGINT, self.sig_handler)

                ioloop.IOLoop.instance().start()
                print('exit...')
            except Exception as ex:
                #print(ex, ex.message)
                print(ex)
            finally:
                os.remove(pid_file)
        else:
            print('pid file exists')

    def initialize(self):
        pass
