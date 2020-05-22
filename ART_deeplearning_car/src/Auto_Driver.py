# -*- coding:utf-8 -*-
"""

"""

import v4l2capture
import sys, select, termios, tty
import os
import time
import threading
from ctypes import *
import numpy as np
import cv2 
from sys import argv


import paddle.fluid as fluid
from PIL import Image
import getopt

#script,vels,save_path= argv

path = os.path.split(os.path.realpath(__file__))[0]+"/.."
opts,args = getopt.getopt(argv[1:],'-hH',['save_path=','vels=','camera='])


camera = "/dev/video0"
save_path = 'model_infer'
vels  = 1545

for opt_name,opt_value in opts:
    if opt_name in ('-h','-H'):
        print("python3 Auto_Driver.py --save_path=%s  --vels=%d --camera=%s "%(save_path , vels , camera))
        exit()
        
    if opt_name in ('--save_path'):
        save_path = opt_value

    if opt_name in ('--vels'):
       vels = int(opt_value)
       
    if opt_name in ('--camera'):
       camera = opt_value


#def load_image(cap):

#    lower_hsv = np.array([156, 43, 46])
#    upper_hsv = np.array([180, 255, 255])
#    lower_hsv1 = np.array([0, 43, 46])
#    upper_hsv1 = np.array([10, 255, 255])
#    ref, frame = cap.read()


#    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)   
#    mask0 = cv2.inRange(hsv, lowerb=lower_hsv, upperb=upper_hsv)
#    mask1 = cv2.inRange(hsv, lowerb=lower_hsv1, upperb=upper_hsv1)
#    mask = mask0 + mask1
#    img = Image.fromarray(mask)
#    img = img.resize((120, 120), Image.ANTIALIAS)
#    img = np.array(img).astype(np.float32)
#    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
#    img = img.transpose((2, 0, 1))
#    img = img[(2, 1, 0), :, :] / 255.0
#    img = np.expand_dims(img, axis=0)
#    return img


def dataset(video): 
    lower_hsv = np.array([15, 90, 165])
    upper_hsv = np.array([0, 255, 255])

    select.select((video,), (), ())        
    image_data = video.read_and_queue()
    
    frame = cv2.imdecode(np.frombuffer(image_data, dtype=np.uint8), cv2.IMREAD_COLOR)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask0 = cv2.inRange(hsv, lowerb=lower_hsv, upperb=upper_hsv)
    #mask1 = cv2.inRange(hsv, lowerb=lower_hsv1, upperb=upper_hsv1)
    mask = mask0 #+ mask1


    img = Image.fromarray(mask)
    img = img.resize((120, 120), Image.ANTIALIAS)
    img = np.array(img).astype(np.float32)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    img = img.transpose((2, 0, 1))
    img = img[(2, 1, 0), :, :] / 255.0
    img = np.expand_dims(img, axis=0)   
    return img

if __name__ == "__main__":
    cout = 0
    save_path  = path + "/model/" + save_path
    
    
    video = v4l2capture.Video_device(camera)
    video.set_format(424,240, fourcc='MJPG')
    video.create_buffers(1)
    video.queue_all_buffers()
    video.start()
   
    
    place = fluid.CPUPlace()
    exe = fluid.Executor(place)
    exe.run(fluid.default_startup_program())
    [infer_program, feeded_var_names, target_var] = fluid.io.load_inference_model(dirname=save_path, executor=exe)


    vel = int(vels)
    lib_path = path + "/lib" + "/libart_driver.so"
    so = cdll.LoadLibrary
    lib = so(lib_path)
    car = "/dev/ttyACM0"

    if (lib.art_racecar_init(38400, car.encode("utf-8")) < 0):
        raise
        pass
    try:
        while 1:
            img = dataset(video)

            result = exe.run(program=infer_program,feed={feeded_var_names[0]: img},fetch_list=target_var)
            angle = result[0][0][0]
            a = int(angle)
            lib.send_cmd(vel, a)
            print(cout)
            cout=cout+1
            print("angle: %d, throttle: %d" % (a, vel))

    except:
        print('error')
    finally:
        lib.send_cmd(1500, 1500)


