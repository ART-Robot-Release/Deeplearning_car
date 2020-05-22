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


class RoadsignLabelHandler(RequestHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    @tornado.gen.coroutine
    def get(self):
        if self.status != 6:
            self.set_status(404, 'system is not in right status.')
            self.write_response({})
            return
        label = json.loads(self.json)['label']
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write_response({'label': label})
        return

