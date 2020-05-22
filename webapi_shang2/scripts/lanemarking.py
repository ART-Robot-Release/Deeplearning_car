# coding=utf8
__author__ = 'quchunyu@baidu.com'

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../website/libraries'))

import errno
import signal
import time
import json
import fcntl
import subprocess
import shutil

import requests

count = 2
while count > 0:
    print('lanemarking - collection', sys.argv)
    time.sleep(5)
    count = count - 1

r = requests.put('http://192.168.1.254/api/system/status',
                 headers={'Content-Type': 'application/json'},
                 data=json.dumps({'status': 3}))
print(r.status_code)
print(r.json())

count = 2
while count > 0:
    print('lanemarking - packaging', sys.argv)
    time.sleep(5)
    count = count - 1

r = requests.put('http://192.168.1.254/api/system/status',
                 headers={'Content-Type': 'application/json'},
                 data=json.dumps({'status': 4, 'data': {'pictures': 555}}))
print(r.status_code)
print(r.json())

exit(0)
