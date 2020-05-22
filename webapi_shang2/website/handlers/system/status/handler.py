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

descriptions = [
    'unknown status',
    'initiative status',
    'edgeboard is in lane-marking status, doing lane-marking collections.',
    'edgeboard has finished lane-marking status, is in post-processing status, doing lane-marking pictures packaging.',
    'edgeboard has finished lane-marking status and post-processes. And pictures package can be downloaded now.',
    'edgeboard road-sign detecting status was received, pre-processing road-sign detection and collections.',
    'edgeboard is in road-sign detecting status, doing road-sign detection. And road-sign pictures and sign-labels \
can be requested. pictures can be selected and released, and further status can be processed.',
    'edgeboard road-sign detecting status was finished, road-sign pictures packaging.',
    'edgeboard has finished roadsign status and its post-processes. And pictures package can be downloaded now.',
    'edgeboard is in models & actions uploading status, and lane-marking, road-sign models and post-detection actions \
package uploading can be requested.',
    'edgeboard is in models running status.',
]


class SystemStatusHandler(RequestHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    @tornado.gen.coroutine
    def get(self):
        description = ''
        payload = {
            'errno': 0,
            'message': 'success',
            'data': {
                'status': self.status,
                'description': descriptions[self.status],
                'data': json.loads(self.json)
            }
        }
        self.write_response(payload)

    @tornado.gen.coroutine
    def options(self):
        self.write_response({})

    @tornado.gen.coroutine
    def post(self):
        self.status = 1
        self.json = json.dumps({})
        payload = {
            'errno': 0,
            'message': 'status was reset to 1 successfully.'
        }
        payload_error = {
            'errno': 1001,
            'message': 'status reset was not supported.'
        }
        Edgeboard.clean_all_processes()
        self.write_response(payload)

    @tornado.gen.coroutine
    def put(self):
        payload_success = {
            'errno': 0,
            'message': 'status was put successfully.'
        }
        payload_error = {
            'errno': 1001,
            'message': 'status putting is not supported.'
        }
        parameter = self.get_parameter()
        print(parameter)
        payload = payload_error
        if self.status == 2:
            if parameter['status'] == 3:
                self.status = parameter['status']
                self.json = json.dumps({})
                payload = payload_success
        elif self.status == 3:
            if parameter['status'] == 4:
                self.status = parameter['status']
                self.json = json.dumps(parameter['data'])
                payload = payload_success
        if self.status == 5:
            if parameter['status'] == 6:
                self.status = parameter['status']
                parameter['data']['totals'] = 0
                self.json = json.dumps(parameter['data'])
                payload = payload_success
        if self.status == 6:
            if parameter['status'] == 6:
                data = json.loads(self.json)
                self.status = parameter['status']
                parameter['data']['totals'] = data['totals']
                self.json = json.dumps(parameter['data'])
                payload = payload_success
        if self.status == 6:
            if parameter['status'] == 7:
                data = json.loads(self.json)
                self.status = parameter['status']
                parameter['data']['totals'] = data['totals']
                self.json = json.dumps(parameter['data'])
                payload = payload_success
        if self.status == 7:
            if parameter['status'] == 8:
                data = json.loads(self.json)
                self.status = parameter['status']
                parameter['data']['totals'] = data['totals']
                self.json = json.dumps(parameter['data'])
                payload = payload_success
        if self.status == 10:
            if parameter['status'] == 1:
                # data = json.loads(self.json)
                self.status = parameter['status']
                self.json = json.dumps({})
                payload = payload_success

        self.write_response(payload)

