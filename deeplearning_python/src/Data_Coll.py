######################################
######ARTRobot DeepLearn Car##########
######Data and Picture Coll V1.0######
#############Steven Zhang#############
##############2019.08.01##############

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import v4l2capture
import select
from ctypes import *
import struct, array
from fcntl import ioctl
import cv2
import numpy as np
import time
from sys import argv
import multiprocessing
import time
import getopt

path = os.path.split(os.path.realpath(__file__))[0]+"/.."

#script, vels = argv
opts,args = getopt.getopt(argv[1:],'-hH',['vels=','output=','serial=','camera=','save_name='])
#print(opts)

camera = multiprocessing.Array("b",range(50))#camera
serial = multiprocessing.Array("b",range(50))#serial
output_data = multiprocessing.Array("b",range(50))#output_data
Speed = multiprocessing.Array("i",range(2))#speed and angle (int)

camera.value = "/dev/video0"
output_data.value = "data"
Speed[0]  = 1560
Speed[1]  = 1500
serial.value = "/dev/ttyUSB0"
save_name="img"

#camera = "/dev/video0"

for opt_name,opt_value in opts:
    if opt_name in ('-h','-H'):
        print("python3 Data_Coll.py --vels=1560 --output=data --serial=/dev/ttyUSB0 --camera=/dev/video0  --save_name=img ")
        exit()

    if opt_name in ('--vels'):
        Speed[0]  = int(opt_value)

    if opt_name in ('--output'):
        output_data.value = opt_value

    if opt_name in ('--serial'):
        serial.value = opt_value

    if opt_name in ('--camera'):
        camera.value = opt_value
        print("camera.value=",camera.value)
        
    if opt_name in ('--save_name'):
        save_name = opt_value
        print("save_name=",save_name)


'''创建一个互斥锁，默认是没有上锁的'''
lock = multiprocessing.Manager().Lock()


#a = multiprocessing.Value("i",0)


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        #print("----- new folder -----")
    #else:
        #print('----- there is this folder -----')

def getvalue():
    import os, struct, array
    from fcntl import ioctl

    print('avaliable devices')

    for fn in os.listdir('/dev/input'):
        if fn.startswith('js'):
            print('/dev/input/%s' % fn)

    axis_states = {}
    button_states = {}

    axis_names = {
        0x00 : 'x',
        0x01 : 'y',
        0x02 : 'z',
        0x03 : 'rx',
        0x04 : 'ry',
        0x05 : 'rz',
        0x06 : 'trottle',
        0x07 : 'rudder',
        0x08 : 'wheel',
        0x09 : 'gas',
        0x0a : 'brake',
        0x10 : 'hat0x',
        0x11 : 'hat0y',
        0x12 : 'hat1x',
        0x13 : 'hat1y',
        0x14 : 'hat2x',
        0x15 : 'hat2y',
        0x16 : 'hat3x',
        0x17 : 'hat3y',
        0x18 : 'pressure',
        0x19 : 'distance',
        0x1a : 'tilt_x',
        0x1b : 'tilt_y',
        0x1c : 'tool_width',
        0x20 : 'volume',
        0x28 : 'misc',
    }
    button_names = {
        0x120 : 'trigger',
        0x121 : 'thumb',
        0x122 : 'thumb2',
        0x123 : 'top',
        0x124 : 'top2',
        0x125 : 'pinkie',
        0x126 : 'base',
        0x127 : 'base2',
        0x128 : 'base3',
        0x129 : 'base4',
        0x12a : 'base5',
        0x12b : 'base6',
        0x12f : 'dead',
        0x130 : 'a',
        0x131 : 'b',
        0x132 : 'c',
        0x133 : 'x',
        0x134 : 'y',
        0x135 : 'z',
        0x136 : 'tl',
        0x137 : 'tr',
        0x138 : 'tl2',
        0x139 : 'tr2',
        0x13a : 'select',
        0x13b : 'start',
        0x13c : 'mode',
        0x13d : 'thumbl',
        0x13e : 'thumbr',

        0x220 : 'dpad_up',
        0x221 : 'dpad_down',
        0x222 : 'dpad_left',
        0x223 : 'dpad_right',

        # XBox 360 controller uses these codes.
        0x2c0 : 'dpad_left',
        0x2c1 : 'dpad_right',
        0x2c2 : 'dpad_up',
        0x2c3 : 'dpad_down',
    }

    axis_map = []
    button_map = []

    fn = '/dev/input/js0'
    jsdev = open(fn, 'rb')

    buf = array.array('u',str(['\0']*5))
    ioctl(jsdev, 0x80006a13 + (0x10000 * len(buf)), buf)
    js_name = buf.tostring()
    #js_name = buf.tobytes().decode('utf-8')
    #print('device name: %s' % js_name)

    # get number of axes and buttons
    buf = array.array('B', [0])
    ioctl(jsdev, 0x80016a11, buf)  # JSIOCGAXES
    num_axes = buf[0]

    buf = array.array('B', [0])
    ioctl(jsdev, 0x80016a12, buf) # JSIOCGBUTTONS
    num_buttons = buf[0]

    # Get the axis map
    buf = array.array('B', [0] * 0x40)
    ioctl(jsdev, 0x80406a32, buf) #JSIOCGAXMAP
    for axis in buf[:num_axes]:
        #print(axis)
        axis_name = axis_names.get(axis, 'unknow(0x%02x)' % axis)
        axis_map.append(axis_name)
        axis_states[axis_name] = 0.0
    
    # Get the button map.
    buf = array.array('H', [0] * 200)
    ioctl(jsdev, 0x80406a34, buf) # JSIOCGBTNMAP

    for btn in buf[:num_buttons]:
        btn_name = button_names.get(btn, 'unknown(0x%03x)' % btn)
        button_map.append(btn_name)
        button_states[btn_name] = 0
    
    return axis_map, axis_states,button_map,button_states
    
    
    
def save_image_process(lock,n,status,start,Camera):

    global path
    global save_name

    mkdir(path+"/data")
    mkdir(path+"/data/"+save_name)

    #video = v4l2capture.Video_device("/dev/video0")
    video = v4l2capture.Video_device(Camera.value)
    video.set_format(1280, 720, fourcc='MJPG')
    video.create_buffers(1)
    video.queue_all_buffers()
    video.start() 
    imgInd = 0
    print("Wait Start!")
    while(start.value == False):
        pass
    while status.value:#PS2 tr or tl control stop
        #print("status",status.value)
        select.select((video,), (), ())        
        image_data = video.read_and_queue()
        frame = cv2.imdecode(np.frombuffer(image_data, dtype=np.uint8), cv2.IMREAD_COLOR)
        cv2.imwrite(path+"/data/"+save_name+"/{}.jpg".format(imgInd), frame)
        #a.value = imgInd
        print("imgInd=",imgInd)
        lock.acquire()
        n.value = True
        lock.release()
        imgInd+=1
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break 
 
def save_data_process(lock,n,data,run):
    #angledata = []
    file_write = open(path+"/data/"+ output_data.value+".txt","a")
    while run.value:        
        while(n.value):          
            lock.acquire()       
            n.value = False
            lock.release()
            print("speed=",data[0],"  angle=",data[1])
            #angledata.append(data[1])
            #angle = np.array(angledata)
            #angle = np.array(data[1])
            #np.save(path+"/data/"+ output_data.value, angle,False)
            file_write.write(str(data[1]))
            file_write.write("\n")
            file_write.flush()       
            

def control_car_process(data,status,run,start):
    max_num = 2100
    min_num = 700
    while run.value:
        speed_car = data[0]
        angle_car = 1500
        fn = '/dev/input/js0'
        jsdev = open(fn, 'rb')
        car = serial.value
        axis_map, axis_states, button_map, button_states = getvalue()
        lib_path = path + "/lib" + "/libart_driver.so"
        so = cdll.LoadLibrary
        lib = so(lib_path)



        try:
            if (lib.art_racecar_init(38400, car.encode("utf-8")) < 0):
                raise
                pass
            lib.send_cmd(1500, 1500)
            while run.value:        
                evbuf = jsdev.read(8)
                if evbuf:
                    time, value, type, number = struct.unpack('IhBB', evbuf)
                    if type & 0x01:
                        button = button_map[number]
                        if button:
                            button_states[button] = value
                            if(button == "b"and button_states[button] == True):
                                start.value = True
                                print("START")
                                lib.send_cmd(speed_car, angle_car)
                            if((button == "tr" and button_states[button] == True) or (button == "tl" and button_states[button] == True)):
                            #Stop 
                                print("Stop")
                                status.value = False
                                data[0] = 1500
                                data[1] = 1500
                                lib.send_cmd(1500, 1500)
                    if(start.value == True):#PS2 control speed and angle start
                        if type & 0x02:
                            axis = axis_map[number]
                            if axis:
                                if axis == "x":

                                    fvalue = value / 32767
                                    axis_states[axis] = fvalue
                                    angle1 = 1500 - (fvalue * 800)
                                    #if angle1 <= 800:
                                    #    angle1 = 800
                                    if angle1 >= 2100:
                                        angle1 = 2100
                                    angle_car = int(angle1)

                                    data[0] = speed_car
                                    data[1] = angle_car
                                    lib.send_cmd(speed_car, angle_car)

 
                #for i in 8:                
                #    evbuf1 = jsdev.read(i)
                #    print("id = ",evbuf1)

        except:
            print("car run error")
        finally:
            lib.send_cmd(1500, 1500)
            print("car run finally")

def txt_2_numpy():
    angledata = []
    data = []
    file = open(path+"/data/"+ output_data.value+".txt","r")
    for line in file.readlines():
        line = line.strip('\n')
        angledata.append(int(line))
    angle = np.array(angledata)
    np.save(path+"/data/"+ output_data.value+".npy", angle,False)
    file.close()


if __name__ == '__main__':
    
    Flag_save_data = multiprocessing.Value("i",False)#New img save flag

    Status = multiprocessing.Value("i",True)#Run or Stop for PS2
    START = multiprocessing.Value("i",False)#START
    RUN = multiprocessing.Value("i",True)#SHUTDOWN

    try:
        process_car = multiprocessing.Process(target=control_car_process,args=(Speed,Status,RUN,START))
        process_image = multiprocessing.Process(target=save_image_process,args=(lock,Flag_save_data,Status,START,camera,))
        process_data = multiprocessing.Process(target=save_data_process,args=(lock,Flag_save_data,Speed,RUN,))
        process_car.start()
        process_image.start()
        process_data.start()



        while(1):
            if(Status.value == 0):
                time.sleep(1)
                RUN.value = False
                print("STOP CAR")
                print("TXT to npy")
                txt_2_numpy()
                break
    except:
        RUN.value = False
        print("error")

    finally:
        RUN.value = False
        print("finally")     

