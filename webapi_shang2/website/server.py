# coding=utf8
__author__ = 'quchunyu@baidu.com'

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libraries'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'handlers'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models'))

import tornado.web

from framework.app import BaseApp

from settings import debug, gzip
from routings import routings


class Api(BaseApp):
    pass


routings.append((r"/(.*)", tornado.web.StaticFileHandler, {'path': 'webroot'}))
print('\n'.join([e[0] for e in routings]))

if __name__ == '__main__':
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        port = int(8899)

    api = Api(
        port=port,
        routings=routings,
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        debug=debug,
        gzip=gzip)

    api.start()
