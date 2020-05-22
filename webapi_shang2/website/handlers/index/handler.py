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

from framework.request_handler import RequestHandler


class IndexHandler(RequestHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    @tornado.gen.coroutine
    def get(self):
        version = {
            'application': 'Edgeboard WebAPI Platform',
            'author': 'quchunyu@baidu.com'
        }
        self.write_response(version)
        # msg = "hello world!"
        # self.render("index.html", info=msg)

