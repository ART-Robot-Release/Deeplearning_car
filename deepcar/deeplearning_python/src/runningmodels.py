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
if sys.argv[1] == True:
    print("roading change")
if sys.argv[2] == False:
    print("detected change ")

'''
count = 4
while count > 0:
    time.sleep(5)
    count = count - 1
'''
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
import sys, select, termios, tty
import threading
#import paddle.fluid as fluid
import paddlemobile as pm
from PIL import Image
import getopt
import codecs
#import paddle
import math
import functools
#from IPython.display import display
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from collections import namedtuple
from datetime import datetime 
import threading
from user import user_cmd

path = os.path.split(os.path.realpath(__file__))[0]+"/.."
lock = multiprocessing.Manager().Lock()
camera = "/dev/video2"
save_path = 'model_infer'
vels  = 1573

def dataset(video): 
    lower_hsv = np.array([156, 43, 46])
    upper_hsv = np.array([180, 255, 255])
    lower_hsv1 = np.array([0, 43, 46])
    upper_hsv1 = np.array([10, 255, 255])
    select.select((video,), (), ())        
    image_data = video.read_and_queue()
    
    frame = cv2.imdecode(np.frombuffer(image_data, dtype=np.uint8), cv2.IMREAD_COLOR)
    #cv2.imwrite("mmmmm2.jpg", frame)

    lock.acquire()
    cv2.imwrite("mmmmm2.jpg", frame)
    lock.release()

    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask0 = cv2.inRange(hsv, lowerb=lower_hsv, upperb=upper_hsv)
    mask1 = cv2.inRange(hsv, lowerb=lower_hsv1, upperb=upper_hsv1)
    mask = mask0 + mask1


    img = Image.fromarray(mask)
    img = img.resize((120, 120), Image.ANTIALIAS)
    img = np.array(img).astype(np.float32)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    img = img.transpose((2, 0, 1))
    img = img[(2, 1, 0), :, :] / 255.0
    img = np.expand_dims(img, axis=0)   
    return img



##################################################################################################人行道检测
#################初始化
train_parameters = {
    "train_list": "train.txt",
    "eval_list": "eval.txt",
    "class_dim": -1,
    "label_dict": {},
    "num_dict": {},
    "image_count": -1,
    "continue_train": True,     # 是否加载前一次的训练参数，接着训练
    "pretrained": False,
    "pretrained_model_dir": "./pretrained-model",
    "save_model_dir": "./yolo-model",
    "model_prefix": "yolo-v3",
    "freeze_dir": "freeze_model",
    #"freeze_dir": "../model/tiny-yolov3",
    "use_tiny": True,          # 是否使用 裁剪 tiny 模型
    "max_box_num": 20,          # 一幅图上最多有多少个目标
    "num_epochs": 80,
    "train_batch_size": 32,      # 对于完整 yolov3，每一批的训练样本不能太多，内存会炸掉；如果使用 tiny，可以适当大一些
    "use_gpu": False,
    "yolo_cfg": {
        "input_size": [3, 448, 448],    # 原版的边长大小为608，为了提高训练速度和预测速度，此处压缩为448
        "anchors": [7, 10, 12, 22, 24, 17, 22, 45, 46, 33, 43, 88, 85, 66, 115, 146, 275, 240],
        "anchor_mask": [[6, 7, 8], [3, 4, 5], [0, 1, 2]]
    },
    "yolo_tiny_cfg": {
        "input_size": [3, 256, 256],
        "anchors": [6, 8, 13, 15, 22, 34, 48, 50, 81, 100, 205, 191],
        "anchor_mask": [[3, 4, 5], [0, 1, 2]]
    },
    "ignore_thresh": 0.7,
    "mean_rgb": [127.5, 127.5, 127.5],
    "mode": "train",
    "multi_data_reader_count": 4,
    "apply_distort": True,
    "nms_top_k": 300,
    "nms_pos_k": 300,
    "valid_thresh": 0.01,
    "nms_thresh": 0.45,
    "image_distort_strategy": {
        "expand_prob": 0.5,
        "expand_max_ratio": 4,
        "hue_prob": 0.5,
        "hue_delta": 18,
        "contrast_prob": 0.5,
        "contrast_delta": 0.5,
        "saturation_prob": 0.5,
        "saturation_delta": 0.5,
        "brightness_prob": 0.5,
        "brightness_delta": 0.125
    },
    "sgd_strategy": {
        "learning_rate": 0.002,
        "lr_epochs": [30, 50, 65],
        "lr_decay": [1, 0.5, 0.25, 0.1]
    },
    "early_stop": {
        "sample_frequency": 50,
        "successive_limit": 3,
        "min_loss": 2.5,
        "min_curr_map": 0.84
    }
}
def init_train_parameters():
    """
    初始化训练参数，主要是初始化图片数量，类别数
    :return:
    """
    file_list = "./data/data6045/train.txt"#os.path.join(train_parameters['data_dir'], train_parameters['train_list'])
    label_list =  "./data/data6045/label_list"#os.path.join(train_parameters['data_dir'], "label_list")
    index = 0
    with codecs.open(label_list, encoding='utf-8') as flist:
        lines = [line.strip() for line in flist]
        for line in lines:
            train_parameters['num_dict'][index] = line.strip()
            train_parameters['label_dict'][line.strip()] = index
            index += 1
        train_parameters['class_dim'] = index
    with codecs.open(file_list, encoding='utf-8') as flist:
        lines = [line.strip() for line in flist]
        train_parameters['image_count'] = len(lines)





def resize_img(img, target_size):
    """
    保持比例的缩放图片
    :param img:
    :param target_size:
    :return:
    """
    img = img.resize(target_size[1:], Image.BILINEAR)
    return img


def read_image():
    """
    读取图片
    :param img_path:
    :return:
    """
    img_path = "/home/root/workspace/aistudio2/src/mmmmm2.jpg" 
    
    lock.acquire()
    origin = Image.open(img_path)
    lock.release()  
  
    #origin = image
    img = resize_img(origin, target_size)
    resized_img = img.copy()
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img = np.array(img).astype('float32').transpose((2, 0, 1))  # HWC to CHW
    img -= 127.5
    img *= 0.007843
    img = img[np.newaxis, :]
    return origin, img, resized_img



video = v4l2capture.Video_device(camera)
video.set_format(424, 240, fourcc='MJPG')
video.create_buffers(1)
video.queue_all_buffers()
video.start()
img=np.zeros((424,240,3))

origin=None
tensor_img=None
resized_img=None


def THREAD():
    global video
    global img
    global origin, tensor_img, resized_img
    nowtime2 = datetime.now()
    while(1):
        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",datetime.now()-nowtime2)
        nowtime2 = datetime.now()
        img = dataset(video)

def THREAD_2():
    global video
    global img
    global origin, tensor_img, resized_img
    nowtime2 = datetime.now()
    while(1):
        print("ddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",datetime.now()-nowtime2)
        nowtime2 = datetime.now()
        origin, tensor_img, resized_img = read_image()

        
        
if __name__ == "__main__":
    
    #################读入图像
    init_train_parameters()
    ues_tiny = train_parameters['use_tiny']
    yolo_config = train_parameters['yolo_tiny_cfg'] if ues_tiny else train_parameters['yolo_cfg']
    target_size = yolo_config['input_size']
    anchors = yolo_config['anchors']
    anchor_mask = yolo_config['anchor_mask']
    label_dict = train_parameters['num_dict']
    class_dim = train_parameters['class_dim']
   
     ############################开启控制进程
    #process_crossing = multiprocessing.Process(target=detection_crossing_process,args=(data1,RUN,STATE))
    #process_crossing.start()
    RUN_value = True#由人行道识别控制
    STATE_value = False#由人行道识别控制
    


    cout = 0
    save_path  = path + "/model/" + save_path
    model_dir = save_path
   
    
    '''place = fluid.CPUPlace()
    exe = fluid.Executor(place)
    exe.run(fluid.default_startup_program())
    [infer_program, feeded_var_names, target_var] = fluid.io.load_inference_model(dirname=save_path, executor=exe,params_filename = model_dir + '/params',model_filename = model_dir + "/model")'''
   
    pm_config = pm.PaddleMobileConfig()
    pm_config.precision = pm.PaddleMobileConfig.Precision.FP32
    pm_config.device = pm.PaddleMobileConfig.Device.kFPGA
    pm_config.prog_file = model_dir + "/model"  
    pm_config.param_file = model_dir + '/params'
    pm_config.thread_num = 4
    
    predictor = pm.CreatePaddlePredictor(pm_config)
    

    vel = int(vels)
    lib_path = path + "/lib" + "/libart_driver.so"
#    so = cdll.LoadLibrary
#    lib = so(lib_path)
#    car = "/dev/ttyUSB0"
    
    #######人行道识别部分——数据处理#######
    path1 = train_parameters['freeze_dir']
    model_dir = path1
    pm_config1 = pm.PaddleMobileConfig()
    pm_config1.precision = pm.PaddleMobileConfig.Precision.FP32######ok
    pm_config1.device = pm.PaddleMobileConfig.Device.kFPGA######ok
    #pm_config.prog_file = model_dir + '/model'
    #pm_config.param_file = model_dir + '/params'
    pm_config1.model_dir = model_dir
    pm_config1.thread_num = 4    
    predictor1 = pm.CreatePaddlePredictor(pm_config1)

    TH_1=threading.Thread(target=THREAD,name='THREAD')
    TH_1.start()
    #TH_2=threading.Thread(target=THREAD_2,name='THREAD_2')
    #TH_2.start()
    time.sleep(1)
    #######目标检测识别部分——控制#######
#    if (lib.art_racecar_init(38400, car.encode("utf-8")) < 0):
#        raise
#        pass
    #try:
    while(1):
        count =0
        nowtime2 = datetime.now()
        yuzhi_0 = 0
        yuzhi_3 =  0
        yuzhi_4 = 0
        while RUN_value:
            print("????????????????????????????????????????????????????????????????????????????????",datetime.now()-nowtime2)
            nowtime2 = datetime.now()
            nowtime = datetime.now()
            #img = dataset(video)
            print("*******************load read_image      cost time:",datetime.now()-nowtime)
            #####################################################################################################################
            #time.sleep(0.05)
            #print("**************************************************************************0")
            nowtime = datetime.now()
            
            origin, tensor_img, resized_img = read_image()
            print(type(origin),type(tensor_img),type(resized_img))
            print("*******************crossing  read_image      cost time:",datetime.now()-nowtime)
            nowtime = datetime.now()
            input_w, input_h = origin.size[0], origin.size[1]
            image_shape = np.array([input_h, input_w], dtype='int32')
            t1 = time.time()
            tensor = pm.PaddleTensor()
            tensor.dtype =pm.PaddleDType.FLOAT32
            #tensor.shape  = (1,3,input_w,input_h)
            tensor.shape  = (1,3,256,256)
            tensor.data = pm.PaddleBuf(tensor_img)
            paddle_data_feeds1 = [tensor]
            
            #print("**************************************************************************1",count)
            count+=1
            #time.sleep(1)  
            #***************
            outputs1 = predictor1.Run(paddle_data_feeds1)
            print("*******************crossing  get_result  cost time:",datetime.now()-nowtime)
            #print("**************************************************************************2")
            assert len(outputs1) == 1, 'error numbers of tensor returned from Predictor.Run function !!!'
            #print("**************************************************************************3")
            bboxes = np.array(outputs1[0], copy = False)
            #print("**************************************************************************4")
            print("bboxes.shape",bboxes.shape)

            t_labels = []
            t_scores = []
            t_boxes = []
            center_x = []
            center_y = []

            if len(bboxes.shape) == 1 :
                print("No object found in video")
                STATE_value =False
            else:
                STATE_value =False
                labels = bboxes[:, 0].astype('int32')
                scores = bboxes[:, 1].astype('float32')
                boxes = bboxes[:, 2:].astype('float32')  
                for i in range(len(labels)):
                    if scores[i] > 0.3 :
                        #t_labels.append(label_dict[labels[i]])
                        t_labels.append(labels[i])
                        t_scores.append(scores[i])
                        center_x.append(int((boxes[i][0]+boxes[i][2])/2))
                        center_y.append((boxes[i][1]+boxes[i][3])/2)
                        STATE_value = True

             

            print("#########crossing   cost time:",datetime.now()-nowtime)
            #####################################################################################################################
            nowtime=datetime.now()
              
            
                
            #result = exe.run(program=infer_program,feed={feeded_var_names[0]: img},fetch_list=target_var)
            #angle = result[0][0][0]
            input = img
            tensor = pm.PaddleTensor()
            tensor.dtype =pm.PaddleDType.FLOAT32
            tensor.shape  = (1,3,120,120)
            tensor.data = pm.PaddleBuf(input)
            #print("image deal----cost_time :",datetime.now()-nowtime)
            paddle_data_feeds = [tensor]
            #############################
            #print("#########crossing  dele_image  cost time:",datetime.now()-nowtime)
            
            nowtime=datetime.now()
            
            outputs = predictor.Run(paddle_data_feeds)
            #print("*******************load     get result :",datetime.now()-nowtime)###################
            #time.sleep(0.01)
            assert len(outputs) == 1
            angle = np.array(outputs[0],copy = False)                
            
            a = int(angle)
            #lib.send_cmd(vel, a)
            #print(cout)
            #cout=cout+1
            print("angle: %d, throttle: %d" % (a, vel))
            print("****************load  cost_time:",datetime.now()-nowtime)

            user_cmd(STATE_value,t_labels,center_x,center_y,vel,a)


    r = requests.put('http://192.168.2.201/api/system/status',
                     headers={'Content-Type': 'application/json'},
                     data=json.dumps({'status': 1}))
    print(r.status_code)
    print(r.json())

    exit(0)
