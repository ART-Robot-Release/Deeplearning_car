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


class RoadsignImageHandler(RequestHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    @tornado.gen.coroutine
    def get(self):
        if self.status != 6:
            self.set_status(404, 'system is not in right status.')
            self.write_response({})
            return
        self.set_header('Content-Type', 'image/jpeg')
        buf_size = 4096
        location = json.loads(self.json)['picture']
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
            self.set_status(404, 'image ' + location + ' not found!')
            self.write_response({})
            return

    @tornado.gen.coroutine
    def options(self):
        self.write_response({})

    @tornado.gen.coroutine
    def post(self):
        if self.status != 6:
            self.set_status(404, 'system is not in right status.')
            self.write_response({})
            return
        payload_success = {
            'errno': 0,
            'message': 'image confirm succeed.'
        }
        payload_failed = {
            'errno': 1006,
            'message': 'invalid arguments.'
        }
        parameter = self.get_parameter()
        if 'action' not in parameter:
            self.write_response(payload_failed)
            return
        if parameter['action'] == 'cancel':
            finished = Edgeboard.image_confirm_roadsign(parameter['action'], None, None, None)
            if finished:
                self.write_response(payload_success)
                return
        elif parameter['action'] == 'ok':
            json_value = json.loads(self.json)
            json_value['totals'] = json_value['totals'] + 1
            self.json = json.dumps(json_value)
            finished = Edgeboard.image_confirm_roadsign(parameter['action'],
                                                        json_value['label'],
                                                        json_value['picture'], None)
            if finished:
                self.write_response(payload_success)
                return
        elif parameter['action'] == 'process':
            number = int(json.loads(self.json)['totals'])
            finished = Edgeboard.image_confirm_roadsign(parameter['action'], None, None, number)
            if finished:
                self.write_response(payload_success)
                return

        self.write_response(payload_failed)
        return


