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


from paddlelite import *
from PIL import Image
import getopt

#script,vels,save_path= argv

path = os.path.split(os.path.realpath(__file__))[0]+"/.."
opts,args = getopt.getopt(argv[1:],'-hH',['save_path=','vels=','camera='])


camera = "/dev/video2"
save_path = 'model_infer'
vels  = 1550
crop_size = 160
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
#    img = img.resize((128, 128), Image.ANTIALIAS)
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
    
    mask = mask0 #+ mask1


    img = Image.fromarray(mask)
    img = img.resize((128, 128), Image.ANTIALIAS)
    #img = cv2.resize(img, (128, 128))
    img = np.array(img).astype(np.float32)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    img = img / 255.0;
    img = np.expand_dims(img, axis=0)
    print("image____shape:",img.shape)
    return img;

def load_model():
    valid_places =   (
		Place(TargetType.kFPGA, PrecisionType.kFP16, DataLayoutType.kNHWC),
		Place(TargetType.kHost, PrecisionType.kFloat),
		Place(TargetType.kARM, PrecisionType.kFloat),
	);
    config = CxxConfig();
    model = save_path;
    model_dir = model;
    config.set_model_file(model_dir + "/model");
    config.set_param_file(model_dir + "/params");
    #config.model_dir = model_dir
    config.set_valid_places(valid_places);
    predictor = CreatePaddlePredictor(config);
    return predictor;
    
def predict(predictor, image, z):
    img = image; 

    i = predictor.get_input(0);
    i.resize((1, 3, 128, 128));
    print("****************************img",img.shape)
    print("****************************img",z.shape)
    z[ 0,0:img.shape[1], 0:img.shape[2] + 0, 0:img.shape[3]] = img
    z = z.reshape(1, 3, 128, 128);
    frame1 = cv2.imdecode(np.frombuffer(img, dtype=np.uint8), cv2.IMREAD_COLOR)
    cv2.imwrite("zzzzz_test.jpg", frame1)
    i.set_data(z)

    predictor.run();
    out = predictor.get_output(0);
    score = out.data()[0][0];
    print(out.data()[0])
    return score;
if __name__ == "__main__":
    cout = 0
    save_path  = path + "/model/" + save_path
    video = v4l2capture.Video_device(camera)
    video.set_format(424,240, fourcc='MJPG')
    video.create_buffers(1)
    video.queue_all_buffers()
    video.start()
   
    ###############################################################################################
    ###############################################################################################
    #place = fluid.CPUPlace()
    #exe = fluid.Executor(place)
    #exe.run(fluid.default_startup_program())
    #[infer_program, feeded_var_names, target_var] = fluid.io.load_inference_model(dirname=save_path, executor=exe)
    ###############################################################################################
    '''##paddle_mobile
    model_dir = save_path
    pm_config = pm.PaddleMobileConfig()
    pm_config.precision = pm.PaddleMobileConfig.Precision.FP32
    pm_config.device = pm.PaddleMobileConfig.Device.kFPGA
    pm_config.prog_file = model_dir + "/model"  
    pm_config.param_file = model_dir + '/params'
    pm_config.thread_num = 4
    predictor = pm.CreatePaddlePredictor(pm_config)'''  
    
    predictor = load_model();
    ################################################################################################
    ################################################################################################
    
    vel = int(vels)
    lib_path = path + "/lib" + "/libart_driver.so"
    so = cdll.LoadLibrary
    lib = so(lib_path)
    car = "/dev/ttyUSB0"

    if (lib.art_racecar_init(38400, car.encode("utf-8")) < 0):
        raise
        pass
    #try:
    z = np.zeros((1, 128, 128, 3))
    while 1:
        while 1:
            nowtime= time.time()
            img = dataset(video)
            ################################################################################################
            #result = exe.run(program=infer_program,feed={feeded_var_names[0]: img},fetch_list=target_var)
            #angle = result[0][0][0]
            '''####paddle_mobile
            input = img
            tensor = pm.PaddleTensor()
            tensor.dtype =pm.PaddleDType.FLOAT32
            tensor.shape  = (1,3,128,128)
            tensor.data = pm.PaddleBuf(input)
            paddle_data_feeds = [tensor]
            outputs = predictor.Run(paddle_data_feeds)
            assert len(outputs) == 1
            angle = np.array(outputs[0],copy = False)
            '''
            z = np.zeros((1, 128, 128, 3))
            angle = predict(predictor, img, z)
            
            ################################################################################################
            
            #a = int(angle*600 + 1200)
            lib.send_cmd(vel, a)
            print(cout)
            cout=cout+1
            print("angle: %d, throttle: %d" % (a, vel))
            print("*****************************************",time.time()-nowtime)
    '''
    except:
        print('error')
    finally:
        lib.send_cmd(1500, 1500)'''
