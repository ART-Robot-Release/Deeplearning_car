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


class RunningmodelsStatusHandler(RequestHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    @tornado.gen.coroutine
    def options(self):
        self.write_response({})

    @tornado.gen.coroutine
    def post(self):
        payload_success = {
            'errno': 0,
            'message': 'status was transmitted to 10 successfully.'
        }
        payload_transmit_failed = {
            'errno': 1009,
            'message': 'status transmit was failed. the status was not 1 or 9.'
        }
        payload_invalid_args = {
            'errno': 1010,
            'message': 'status transmit was failed. invalid arguments'
        }
        parameter = self.get_parameter()
        if 'lanemarking' not in parameter or   \
           'roadsign' not in parameter:
            payload = payload_invalid_args
            self.write_response(payload)
            return

        if self.status == 1 or self.status == 9:
            finished = Edgeboard.start_runningmodels(parameter['lanemarking'],
                                                     parameter['roadsign'])
            if finished:
                self.status = 10
                self.json = json.dumps({'lanemarking': parameter['lanemarking'],
                                        'roadsign': parameter['roadsign']})
                payload = payload_success
            else:
                payload = payload_invalid_args
        else:
            payload = payload_transmit_failed

        self.write_response(payload)

