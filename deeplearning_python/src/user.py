import os
import cv2
import numpy as np
import time
import sys, select, termios, tty
from ctypes import *
path = os.path.split(os.path.realpath(__file__))[0]+"/.."
lib_path = path + "/lib" + "/libart_driver.so"
so = cdll.LoadLibrary
lib = so(lib_path)
car = "/dev/ttyUSB0"
if (lib.art_racecar_init(38400, car.encode("utf-8")) < 0):
    raise
    pass


label_ten=0
label_xx=0
number = 0
detect =True
nowtime11 = time.time()
def user_cmd(state,labels,scores,center_x,center_y,pre_vel,pre_angle):
    global label_ten
    global label_xx
    global number
    global detect  
    global nowtime11
    print("******************************************angle: %d, throttle: %d" % (pre_angle, pre_vel))
    if state==True:
        '''##########################################'''
        '''0 cancel_10
        1 crossing
        2 limit_10
        3 straight
        4 turn_left
        5 turn_right
        6 paper_red
        7 paper_green'''
        if(detect == True):
            for i in range(len(labels)):
                if(labels[i]==1):
                    if(scores[i]>0.05):
                        if (number < 2):
                            '''#30########################'''
                            number+=1
                            print("******************************number:",number)
                        else:
                            number = 1
                            detect = False
                            nowtime11 = time.time()
                            nowetime2 = time.time()
                            while (time.time()-nowetime2  < 2):
                                print("sleep  sleep  sleep")
                                lib.send_cmd(1500, 1500)
                    else:
                        lib.send_cmd(pre_vel, pre_angle)
                else:
                    lib.send_cmd(pre_vel, pre_angle)
        if(detect == False): 
            if (time.time()-nowtime11 > 10.0):
                detect = True     
            else:
                print("*******************ignore  detect")
                lib.send_cmd(pre_vel, pre_angle)
    else:    
        lib.send_cmd(pre_vel, pre_angle)
        #print("******************************************angle: %d, throttle: %d" % (a, vel))