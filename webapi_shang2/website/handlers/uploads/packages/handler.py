#coding=utf8
from typing import Optional, Awaitable

__author__ = 'quchunyu@baidu.com'

import os
import sys

import time
import json
import traceback
import file_util
import tarfile
import zipfile
import tornado.web
import tornado.gen

from framework.edgeboard import Edgeboard
from framework.request_handler import RequestHandler


class UploadsPackagesHandler(RequestHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    @tornado.gen.coroutine
    def options(self):
        self.write_response({})

    @tornado.gen.coroutine
    def post(self):
        if self.status != 9:
            self.set_status(404, 'system is not in right status.')
            self.write_response({})
            return
        file_metas = self.request.files.get('files', None)
        payload = {'files': ''}
        if not file_metas:
            self.set_status(404)
            self.write_response({})
            return

        file_data_list = []
        tmp_dir = '../scripts/' + self.request.path.split('/')[-1].strip() + '/'
        for meta in file_metas:
            filename = meta['filename']
            content_type = meta['content_type']
            file_path = os.path.normpath(
                os.path.join(tmp_dir, filename))
            with open(file_path, 'wb') as up:
                up.write(meta['body'])

            (file_pure_path, temp_filename) = os.path.split(file_path)
            (file_base_name, file_extension) = os.path.splitext(temp_filename)

            if content_type == 'application/gzip':
                (file_base_name, file_extension) = os.path.splitext(file_base_name)
                with tarfile.open(file_path, 'r') as tar_file:
                    tar_file.extractall(os.path.join(file_pure_path, file_base_name))
            if content_type == 'application/x-tar':
                with tarfile.open(file_path, 'r') as tar_file:
                    tar_file.extractall(os.path.join(file_pure_path, file_base_name))
            if content_type == 'application/zip':
                with zipfile.ZipFile(file_path, 'r') as zip_file:
                    zip_file.extractall(os.path.join(file_pure_path, file_base_name))

            file_size = file_util.get_file_size(file_path)
            file_data = {
                'name': filename,
                'url': "/api/uploads/packages/" + self.request.path.split('/')[-1].strip() + '/' + filename,
                'type': content_type,
                'size': file_size
            }
            file_data_list.append(file_data)

        if len(file_data_list) > 0:
            payload['files'] = file_data_list
            response = {'errno': 0, 'message': 'success', 'data': payload}
        else:
            response = {'errno': 1009, 'message': 'uploaded files invalid.'}

        self.write_response(response)
        return

