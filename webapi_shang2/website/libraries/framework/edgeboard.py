# -*- coding: utf-8 -*-
__author__ = 'quchunyu@baidu.com'

import logging
import os
import signal
import time
import subprocess

from tornado import ioloop
from tornado import web
from tornado.httpserver import HTTPServer

process_lanemarking = None
process_roadsign = None
process_runningmodels = None


class Edgeboard(object):

    @classmethod
    def clean_all_processes(cls):
        global process_lanemarking
        global process_roadsign
        global process_runningmodels

        while process_lanemarking:
            poll = process_lanemarking.poll()
            if poll is not None:
                # print('process_roadsign is dead!')
                process_lanemarking = None
            else:
                # print('process_roadsign is active alive!')
                process_lanemarking.terminate()
                process_lanemarking.wait()
        while process_roadsign:
            poll = process_roadsign.poll()
            if poll is not None:
                # print('process_roadsign is dead!')
                process_roadsign = None
            else:
                # print('process_roadsign is active alive!')
                process_roadsign.terminate()
                process_roadsign.wait()
        while process_runningmodels:
            poll = process_runningmodels.poll()
            if poll is not None:
                # print('process_runningmodels is dead!')
                process_runningmodels = None
            else:
                # print('process_runningmodels is active alive!')
                process_runningmodels.terminate()
                process_runningmodels.wait()

        return True

    @classmethod
    def start_lanemarking(cls, speed, camera, downusb, location):
        global process_lanemarking

        obj_args = {
            # 'stdout': subprocess.PIPE,
            'universal_newlines':   True
        }
        print(process_lanemarking)

        if process_lanemarking:
            poll = process_lanemarking.poll()
            if poll is not None:
                process_lanemarking = None
            else:
                return False

        if process_lanemarking is None:
            os.chdir('../../deeplearning_python/src')
            process_lanemarking = subprocess.Popen(['python', 'lanemarking.py', str(speed), camera, downusb, location],
                                                   **obj_args)
            print('starting lanemarking ...')
            os.chdir('../../webapi/scripts')
            os.chdir('../website')
            return True

        return False

    @classmethod
    def start_roadsign(cls, camera, downusb, location):
        global process_roadsign

        obj_args = {
            'stdin':  subprocess.PIPE,
            # 'stdout': subprocess.PIPE,
            # 'stderr': subprocess.PIPE,
            'universal_newlines':   True,
        }
        print(process_roadsign)

        if process_roadsign:
            poll = process_roadsign.poll()
            if poll is not None:
                process_roadsign = None
            else:
                return False

        if process_roadsign is None:
            os.chdir('../../pd')
            #os.chdir('../scripts')
            process_roadsign = subprocess.Popen(['python', 'roadsign.py', camera, downusb, location],
                                                **obj_args)
            print('starting roadsign ...')
            os.chdir('../webapi/scripts')
            os.chdir('../website')
            return True

        return False

    @classmethod
    def start_runningmodels(cls, lanemarking, roadsign):
        global process_runningmodels

        print(lanemarking)
        print(roadsign)

        obj_args = {
            'stdin':  subprocess.PIPE,
            # 'stdout': subprocess.PIPE,
            # 'stderr': subprocess.PIPE,
            'text':   True,
        }
        print(process_runningmodels)

        if process_runningmodels:
            poll = process_runningmodels.poll()
            if poll is not None:
                process_runningmodels = None
            else:
                return False

        if process_runningmodels is None:
            os.chdir('../scripts')
            print('starting runningmodels ...')
            process_runningmodels = subprocess.Popen(['python', 'runningmodels.py',
                                                      str(lanemarking), str(roadsign)],
                                                     **obj_args)
            os.chdir('../website')
            '''
            os.chdir('../../deeplearning_python/src')
            process_runningmodels = subprocess.Popen(['python', 'runningmodels.py',
                                                      str(lanemarking), str(roadsign)],
                                                     **obj_args)
            print('starting lanemarking ...')
            os.chdir('../../webapi/scripts')
            
            os.chdir('../website')'''
            
            return True

        return False

    @classmethod
    def image_confirm_roadsign(cls, confirm, label, image, number):
        global process_roadsign

        print(process_roadsign)
        if process_roadsign:
            print(process_roadsign.pid)

        if process_roadsign is None:
            return False
        if process_roadsign:
            poll = process_roadsign.poll()
            if poll is not None:
                print('process_roadsign is dead!')
                process_roadsign = None
                return False
            else:
                print('process_roadsign is active alive!')

        if confirm == 'ok' or confirm == 'cancel':
            process_roadsign.stdin.write(confirm + '\n')
            process_roadsign.stdin.flush()
            # print(process_roadsign.stdout.read())
            return True
        elif confirm == 'process':
            process_roadsign.stdin.write(confirm + ' ' + str(number) + '\n')
            process_roadsign.stdin.flush()
            # print(process_roadsign.stdout.read())
            return True

        return False


