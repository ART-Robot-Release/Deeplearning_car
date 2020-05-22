#coding=utf8
"""
    provides global functional functions
"""

import urllib
import urllib2
import traceback
import datetime
import confs.conf

def post_formdata(url, data):
    """
        post data to specified url
    """
    try:
        header = {
            'Content-Type':'application/x-www-form-urlencoded;charset=utf-8'
        }
        endata = urllib.urlencode(data)
        req = urllib2.Request(url, endata, header)
        resp = urllib2.urlopen(req)
        body = resp.read()
        return body
    except:
        traceback.print_exc()
        return False


def post_jsondata(url, jsondata):
    """
        post data to url
    """
    try:
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/json')
        resp = urllib2.urlopen(req, data=jsondata)
        body = resp.read()
        return body
    except:
        traceback.print_exc()
        return False


def get_curtime_str(fmt='%Y%m%d%H%M%S'):
    """
        generate current time to str,
        eg, 2016-01-01 11:12:13 to 20160101111213,
        this str is used as index in db
    """
    stime = datetime.datetime.now().strftime(fmt)
    return stime


def get_curtime_std(fmt='%Y-%m-%d %H:%M:%S'):
    """
        generate current time in standard format
    """
    stime = datetime.datetime.now().strftime(fmt)
    return stime


def uuid():
    """
        calc uuid value
    """
    import uuid as s_uuid
    while True:
        uuid4 = s_uuid.uuid4()
        long1 = long(str(uuid4).replace('-', '')[:16], 16)
        long2 = long(str(uuid4).replace('-', '')[16:], 16)
        h = long1 ^ long2
        if h < 9223372036854775807:
            return str(h)