# -*- coding: utf-8 -*-
"""
    Named Pipe Operations
"""
__author__ = 'quchunyu@baidu.com'

import logging
import os
import signal
import time
import json

from tornado import ioloop
from tornado import web
from tornado.httpserver import HTTPServer


class NamedPipe:
    """
        NamedPipe  a wrapper for a simple client-end named pip
    """
    def __init__(self, application, read_path, write_path):
        """
        constructor
        :param application: tornado's web.Application
        :param read_path: named pipe's reader end
        :param write_path: named pipe's writer end
        """
        self.application = application
        self.read_path = read_path
        self.write_path = write_path

        self.factory_default_status = 0
        self.restart_status = 0
        self.reload_configuration_status = 0

        print(read_path, ' ', write_path)
        print('')
        self.pipe_out = os.open(self.write_path, os.O_SYNC | os.O_CREAT | os.O_RDWR)
        self.pipe_in = os.open(self.read_path, os.O_RDONLY)

    def send(self, request):
        """
        send
        :param request:
        :return: None
        """
        os.write(self.pipe_out, request.encode())

    def receive(self):
        """
        receive
        :return: bytestring
        """
        response = os.read(self.pipe_in, 2048)
        return response.decode()

    def set_time(self, current_time):
        """
        set_time
        :param current_time:
        :return: 0 -- success   others -- errors
        """
        request = 'set-time|' + json.dumps(current_time)
        self.send(request)
        response = self.receive()
        value = json.loads(response)
        return value['value']

    def set_ip(self, ip_address):
        """
        set_ip
        :param ip_address:
        :return: 0 -- success   others -- errors
        """
        request = 'set-ip|' + json.dumps(ip_address)
        self.send(request)
        response = self.receive()
        value = json.loads(response)
        return value['value']

    def upload_verify(self, file_uploaded):
        """
        upload_verify
        :param file_uploaded:  file_uploaded
        :return: 0 -- success   others -- errors
        """
        request = 'upload-verify|' + json.dumps(file_uploaded)
        self.send(request)
        response = self.receive()
        value = json.loads(response)
        return value['value']

    def factory_default(self):
        """
        factory_default
        :return: 0: already in factory_defaulting, 1: perform begins
        """
        if self.factory_default_status == 1:
            return 0
        else:
            self.factory_default_status = 1
            request = 'set-factory-default'
            self.send(request)
            response = self.receive()
            value = json.loads(response)
            self.factory_default_status = 0
            return 1 if value['value'] == 0 else 0

    def reload_configuration(self):
        """
        reload_configuration
        :return: 0 -- success   others -- errors
        """
        if self.reload_configuration_status == 1:
            return 0
        else:
            self.reload_configuration_status = 1
            request = 'reload-configuration'
            self.send(request)
            response = self.receive()
            value = json.loads(response)
            self.reload_configuration_status = 0
            return 1 if value['value'] == 0 else 0

    def restart(self):
        """
        restart
        :return: 0 -- success   others -- errors
        """
        print("before reload_configuration")
        self.reload_configuration()
        print("after reload_configuration")
        if self.restart_status == 1:
            return 0
        else:
            self.restart_status = 1
            request = 'restart'
            self.send(request)
            response = self.receive()
            value = json.loads(response)
            self.restart_status = 0
            return 1 if value['value'] == 0 else 0






