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
    time.sleep(5)
    count = count - 1

r = requests.put('http://192.168.1.254/api/system/status',
                 headers={'Content-Type': 'application/json'},
                 data=json.dumps({'status': 6, 'data': {'picture': 'warning.jpg', 'label': 'warning'}}))

pic = 'W'
number = None

for line in sys.stdin:
    if line.rstrip() == 'ok' or line.rstrip() == 'cancel':
        print(line.lower(), end='\t', file=sys.stdout, flush=True)
        if pic == 'W':
            r = requests.put('http://192.168.1.254/api/system/status',
                             headers={'Content-Type': 'application/json'},
                             data=json.dumps({'status': 6, 'data': {'picture': 'hot.jpg', 'label': 'hot'}}))
            pic = 'H'
        else:
            r = requests.put('http://192.168.1.254/api/system/status',
                             headers={'Content-Type': 'application/json'},
                             data=json.dumps({'status': 6, 'data': {'picture': 'warning.jpg', 'label': 'warning'}}))
            pic = 'W'
    if line.rstrip()[:7] == 'process':
        print(line.lower(), end='\t', file=sys.stdout, flush=True)
        number = int(line.rstrip()[8:])
        r = requests.put('http://192.168.1.254/api/system/status',
                         headers={'Content-Type': 'application/json'},
                         data=json.dumps({'status': 7, 'data': {'totals-packaging': number}}))
        break

count = 2
while count > 0:
    time.sleep(5)
    count = count - 1

r = requests.put('http://192.168.1.254/api/system/status',
                 headers={'Content-Type': 'application/json'},
                 data=json.dumps({'status': 8, 'data': {'totals-packaged': number}}))

exit(0)
