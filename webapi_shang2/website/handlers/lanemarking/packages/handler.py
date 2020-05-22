#coding=utf8
from typing import Optional, Awaitable

__author__ = 'quchunyu@baidu.com'

import os
import sys

import time
import json
import traceback

import tornado.web
import tornado.gen

from framework.edgeboard import Edgeboard
from framework.request_handler import RequestHandler


class LanemarkingPackagesHandler(RequestHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    @tornado.gen.coroutine
    def get(self, location):
        if self.status != 4:
            self.set_status(404, 'system is not in right status.')
            self.write_response({})
            return
        if location is None or location == '':
            self.set_status(404, 'empty package name.')
            self.write_response({})
            return
        if location[-4:] == '.zip':
            self.set_header('Content-Type', 'application/zip')
        else:
            self.set_header('Content-Type', 'application/octet-stream')
        buf_size = 4096
        filename = os.path.normpath(os.getcwd() + '/../scripts/' + location)
        if os.path.isfile(filename):
            print(filename)
            with open(filename, 'rb') as f:
                while True:
                    data = f.read(buf_size)
                    if not data:
                        break
                    self.write(data)
            self.finish()
            return
        else:
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            self.set_status(404, 'package ' + location + ' not found!')
            self.write_response({})
            return

