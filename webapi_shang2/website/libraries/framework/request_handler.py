#coding=utf8
"""
    RequestHandler
"""
__author__ = 'quchunyu@baidu.com'

import os
import sys

import time
import datetime
import json
import traceback
import string
from typing import Optional, Awaitable

import tornado.web
import tornado.gen


class RequestHandler(tornado.web.RequestHandler):

    class ComplexEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime.datetime):
                return obj.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(obj, datetime.date):
                return obj.strftime('%Y-%m-%d')
            else:
                return json.JSONEncoder.default(self, obj)

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.service = None

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    @property
    def status(self):
        """
        status property
        :return: Status
        """
        return self.application.status

    @status.setter
    def status(self, value):
        self.application.status = value

    @status.deleter
    def status(self):
        del self.application.status

    @property
    def json(self):
        return self.application.json

    @json.setter
    def json(self, value):
        self.application.json = value

    @json.deleter
    def json(self):
        del self.application.json

    @property
    def pipe(self):
        """
        pipe property
        :return: NamedPipe
        """
        return self.application.pipe

    def initialize(self, params):
        self.service = params

    def get_parameter(self):
        print('----------------------------- request.method ---------------------------------')
        print(self.request.method)
        print('------------------------------ request.url -----------------------------------')
        print(self.request.full_url())
        print('----------------------------- request.headers --------------------------------')
        print(self.request.headers)
        print('------------------------------ request.body ----------------------------------')
        print(self.request.body)
        print('------------------------------------------------------------------------------')
        parameter = None
        if self.request.method in ("GET", "HEAD"):
            parameter = {k: v[0] for k, v in self.request.arguments.items()}
        else:
            if self.request.headers['Content-Type'].split(";")[0] == 'application/json':
                parameter = json.loads(self.request.body.decode('utf-8'))
            elif self.request.headers['Content-Type'].split(";")[0] == 'application/x-www-form-urlencoded':
                parameter = {}
                items = self.request.body.decode('utf-8').split('&')
                for item in items:
                    value = item.split('=')
                    if value != ['']:
                        parameter[value[0]] = value[1]
            elif self.request.headers['Content-Type'].split(";")[0] == 'multipart/form-data':
                parameter = {}
                boundary = self.request.headers['Content-Type'].split(";")[1].split("=")[1]
                sentences = filter(lambda item: string.strip(item), self.request.body.decode('utf-8').split('--' + boundary))
                sentences = map(lambda item: item.strip('\r\n'), sentences)
                sentences = filter(lambda item: item != '--', sentences)
                for sentence in sentences:
                    contents = sentence.split(';')[1].split('=')[1].split('\r\n\r\n')
                    if len(contents) == 1:
                        parameter[contents[0].strip('\"')] = ''
                    else:
                        parameter[contents[0].strip('\"')] = contents[1]
            else:
                parameter = {}
        
        # print('------------------------ RequestHandler.parameter ----------------------------')
        # print(parameter)
        # print('------------------------------------------------------------------------------')

        return parameter

    @staticmethod
    def fill_response(response, code=0, httpstatus=200, message='ok', data=None):
        response['code'] = code
        response['httpstatus'] = httpstatus
        response['message'] = message
        if data is not None:
            response['data'] = data

    def write_response(self, response):
        self.write(json.dumps(response, cls=RequestHandler.ComplexEncoder))
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Method", "POST,GET,OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.finish()

    def check_login(self):
        """
        check_login
        :return: True is login
        """
        if not self.current_user:
            #self.redirect("/api/system/login")
            result_info = {}
            result_info['errno'] = 1005
            result_info['message'] = "user not login"
            self.write(json.dumps(result_info, indent = 4))
            return False
        return True

    def get_current_user(self):
        print("RequestHandler get_current_user")
        user_cookie = self.get_secure_cookie("user")
        print("user_cookie is:")
        print(user_cookie)
        return user_cookie
