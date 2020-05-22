#coding=utf8
"""
    web system routings
"""
__author__ = 'quchunyu@baidu.com'

import os
import sys

import time
import json
import traceback

import tornado.web
import tornado.gen

from index.handler import IndexHandler
from system.status.handler import SystemStatusHandler
from lanemarking.status.handler import LanemarkingStatusHandler
from lanemarking.packages.handler import LanemarkingPackagesHandler
from roadsign.status.handler import RoadsignStatusHandler
from roadsign.image.handler import RoadsignImageHandler
from roadsign.label.handler import RoadsignLabelHandler
from roadsign.packages.handler import RoadsignPackagesHandler
from uploads.status.handler import UploadsStatusHandler
from uploads.packages.handler import UploadsPackagesHandler
from runningmodels.status.handler import RunningmodelsStatusHandler

routings = [
    (r"/", IndexHandler, dict(params=None)),
    (r"/api/system/status", SystemStatusHandler, dict(params=None)),
    (r"/api/lanemarking/status", LanemarkingStatusHandler, dict(params=None)),
    (r"/api/lanemarking/packages/(.*)", LanemarkingPackagesHandler, dict(params=None)),
    (r"/api/roadsign/status", RoadsignStatusHandler, dict(params=None)),
    (r"/api/roadsign/image", RoadsignImageHandler, dict(params=None)),
    (r"/api/roadsign/label", RoadsignLabelHandler, dict(params=None)),
    (r"/api/roadsign/packages/(.*)", RoadsignPackagesHandler, dict(params=None)),
    (r"/api/uploads/status", UploadsStatusHandler, dict(params=None)),
    (r"/api/uploads/packages/lanemarking", UploadsPackagesHandler, dict(params=None)),
    (r"/api/uploads/packages/roadsign", UploadsPackagesHandler, dict(params=None)),
    (r"/api/uploads/packages/actions", UploadsPackagesHandler, dict(params=None)),
    (r"/api/runningmodels/status", RunningmodelsStatusHandler, dict(params=None)),
]

