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

print('runningmodels - ', sys.argv)
'''if argv[0] = True：
    print ("model")#切换路径
if argv[1] = True：
    print ("model")#切换路径'''
count = 4
while count > 0:
    time.sleep(5)
    count = count - 1

r = requests.put('http://192.168.1.254/api/system/status',
                 headers={'Content-Type': 'application/json'},
                 data=json.dumps({'status': 1}))
print(r.status_code)
print(r.json())

exit(0)
