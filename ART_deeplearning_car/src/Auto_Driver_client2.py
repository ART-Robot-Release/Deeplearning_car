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
import socket

import struct, array
from fcntl import ioctl
import time
import multiprocessing
'''global quality'''
path = os.path.split(os.path.realpath(__file__))[0]+"/.."
save_path = 'model_infer'
'''multi  processing'''
camera = multiprocessing.Array("b",range(50))#output_data
serial = multiprocessing.Array("b",range(50))#serial
Output_data0 = multiprocessing.Array('u', 500)
Output_data1 = multiprocessing.Array("i",range(2))

Speed = multiprocessing.Array("i",range(2))#speed and angle (int)
NUM = multiprocessing.Array("i",range(2))


camera.value = "/dev/video0"
serial.value = "/dev/ttyACM0"

mm = "label"
for i in range(len(mm)):    
    Output_data0[i] = mm[i]
Output_data0[i+1] = '$'
'''
strPath = ''
for i in range(0,500):
    if Output_data0[i] =='$':
        break
    else:
        strPath += Output_data0[i]
print("********************************************************************",strPath)'''


Output_data1[0] = 0
Output_data1[1] = 0
Speed[0]  = 1540
Speed[1]  = 1500
NUM.value = 0

save_name="img"
'''define input label'''
opts,args = getopt.getopt(argv[1:],'-hH',['serial=','vels='])
for opt_name,opt_value in opts:
    if opt_name in ('-h','-H'):
        print("python3 Auto_Driver_client2.py   --serial=%s  --vels=%d  "%(serial , vels ))
        exit()    
    if opt_name in ('--serial'):
        serial = opt_value
    if opt_name in ('--vels'):
       Speed[0] = int(opt_value)
'''LOCK image save  or  get '''
lock = multiprocessing.Manager().Lock()
'''LOCK tcp date  save  or  get '''
lock1 = multiprocessing.Manager().Lock()
def dataset(frame): 
    lower_hsv = np.array([15, 90, 165])
    upper_hsv = np.array([0, 255, 255])

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lowerb=lower_hsv, upperb=upper_hsv)

    img = Image.fromarray(mask)
    img = img.resize((120, 120), Image.ANTIALIAS)
    img = np.array(img).astype(np.float32)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    img = img.transpose((2, 0, 1))
    img = img[(2, 1, 0), :, :] / 255.0
    img = np.expand_dims(img, axis=0)   
    return img
'''########################GET TCP DATA########################'''
def get_data_process(run,output_data0,output_data1,num,lock1):
    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_client.connect(('127.0.0.1',1234))
    num.value = 0
    while run.value:
        num.value += 1
        recv_ = tcp_client.recv(1024) 
        recv_data = recv_.decode('utf-8')
        print ("*****open tcp ")
        if(len(recv_data)>20):
            print(len(recv_data))
            continue
        if(recv_data.find('null') == -1):
            classes,center_x,center_y=recv_data.split(',',2) 
            lock1.acquire()       
            
            #output_data0.value=  classes
            for i in range(len(classes)):    
                Output_data0[i] = classes[i]
            Output_data0[i+1] = '$'
            
            output_data1[0] =  int(center_x)
            output_data1[1] =  int(center_y)
            lock1.release()

            strPath = ''
            for i in range(0,500):
                if Output_data0[i] =='$':
                    break
                else:
                    strPath += Output_data0[i]
            
            #print("get data {},{},{}".format(strPath,output_data1[0],output_data1[1]))
'''########################GET IMAGE DATA########################'''
def save_image_process(lock,camera,run,state):
    global path
    video = v4l2capture.Video_device(camera.value)
    video.set_format(424,240, fourcc='MJPG')
    video.create_buffers(50)
    video.queue_all_buffers()
    video.start()
    while run.value:
        while (state.value == True):
            nowtime1 = time.time()
            select.select((video,), (), ())        
            image_data = video.read_and_queue()            
            frame1 = cv2.imdecode(np.frombuffer(image_data, dtype=np.uint8), cv2.IMREAD_COLOR)
            '''SAVE IMAGE TO LOCAL'''
            lock.acquire()       
            cv2.imwrite(path+"/1.jpg", frame1)
            state.value = False
            lock.release()
            print("get  image process cost :",1/float(time.time()-nowtime1))
'''########################CONTRAL CAR RUN  ########################'''
def control_car_process(lock,speed,run,num,output_data0,output_data1,state,lock1,serial):#
    global path
    global save_path 
    save_path  = path + "/model/" + save_path
    
    place = fluid.CPUPlace()
    exe = fluid.Executor(place)
    exe.run(fluid.default_startup_program())
    [infer_program, feeded_var_names, target_var] = fluid.io.load_inference_model(dirname=save_path, executor=exe)
    
    vel = speed[0]
    lib_path = path + "/lib" + "/libart_driver.so"
    so = cdll.LoadLibrary
    lib = so(lib_path)
    car = "/dev/ttyACM0"   
    if (lib.art_racecar_init(38400, car.encode("utf-8")) < 0):
        raise
        pass
        
    get_tcp = False
    a = num.value
    #time.sleep(2)
    detect =  True
    number = 1
    number_cancel = 1 
    number_green = 1
    number_red = 1
    number_limit = 1 
    #try:
    while 1:
        while run.value:  
           while state.value == False:                      
                nowtime = time.time()
                '''tcp data'''
                if (a != num.value):
                    get_tcp = True
                    a = num.value
                    
                    
                    lock1.acquire()
                    #classes = output_data0
                    
                    strPath = ""
                    for i in range(0,500):
                        if Output_data0[i] =='$':
                            break
                        else:
                            strPath += Output_data0[i]
                    classes =  strPath       
                    center_x = output_data1[0]
                    center_y  = output_data1[1]
                    lock1.release()
                    print("*************************************************************************************get data {},{},{}".format(classes,center_x,center_y))
                ''' image data  '''      
                lock.acquire()           
                frame = cv2.imread(path+"/1.jpg")
                state.value = True
                lock.release()
                
                img = dataset(frame)
                result = exe.run(program=infer_program,feed={feeded_var_names[0]: img},fetch_list=target_var)
                angle = result[0][0][0]
                '''recovery to  1200---1800'''
                #a = int(angle*600+1200)
                a = int(angle)
                if (get_tcp == True):
                    '''GET TCP IMG****************************************************************DO SOMETHING'''
                  
                                              
                '''GET TCP IMG****************************************************************DO SOMETHING''' 
                get_tcp = False 
                print('******output: speed = {} ,angle = {}'.format(vel, a))
                lib.send_cmd(vel, a)
                print("*****************************************  the test   rate",1/float(time.time()-nowtime))
                
    '''except:
        print("car run error")
    finally:
        lib.send_cmd(1500, 1500)
        print("car run finally")  '''     
        
if __name__ == "__main__":
 
    lib_path = path + "/lib" + "/libart_driver.so"
    so = cdll.LoadLibrary
    lib = so(lib_path)
    
    RUN = multiprocessing.Value("i",True)#SHUTDOWN
    STATE = multiprocessing.Value("i",True)# 
    try:
        while(1):    
            process_tcp = multiprocessing.Process(target=get_data_process,args=(RUN,Output_data0,Output_data1,NUM,lock1))
            process_image = multiprocessing.Process(target=save_image_process,args=(lock,camera,RUN,STATE))
            process_car = multiprocessing.Process(target=control_car_process,args=(lock,Speed,RUN,NUM,Output_data0,Output_data1,STATE,lock1,serial))#
            
            process_tcp.start()
            process_image.start()
            process_car.start()
            
            while(1):
                {}
          
    except:
        RUN.value = False
        time.sleep(1)
        lib.send_cmd(1500, 1500)
        print("error")

    finally:
        RUN.value = False
        time.sleep(1)
        lib.send_cmd(1500, 1500)
        print("finally")    
    

