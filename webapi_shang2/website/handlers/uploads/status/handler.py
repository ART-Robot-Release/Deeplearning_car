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


class UploadsStatusHandler(RequestHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    @tornado.gen.coroutine
    def options(self):
        self.write_response({})

    @tornado.gen.coroutine
    def post(self):
        payload_success = {
            'errno': 0,
            'message': 'status was transmitted to 9 successfully.'
        }
        payload_transmit_failed = {
            'errno': 1007,
            'message': 'status transmit was failed. the status was not 1.'
        }
        payload_invalid_args = {
            'errno': 1008,
            'message': 'status transmit was failed. invalid arguments'
        }

        if self.status == 1:
            finished = Edgeboard.clean_all_processes()
            if finished:
                self.status = 9
                self.json = json.dumps({})
                payload = payload_success
            else:
                payload = payload_invalid_args
        else:
            payload = payload_transmit_failed

        self.write_response(payload)

