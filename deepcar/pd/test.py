# -*- coding: UTF-8 -*-
"""
训练常基于dark-net的YOLOv3网络，目标检测
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os
os.environ["FLAGS_fraction_of_gpu_memory_to_use"] = '0.82'
import uuid
import numpy as np
import time
import six
import math
import random
#import paddle
#import paddle.fluid as fluid
import logging
import xml.etree.ElementTree
import codecs
import json
import cv2
import paddlemobile as pm
#from paddle.fluid.initializer import MSRA
#from paddle.fluid.param_attr import ParamAttr
#from paddle.fluid.regularizer import L2Decay
from PIL import Image, ImageEnhance, ImageDraw

# logger = None
train_parameters = {
    "data_dir": "data",
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
    "use_tiny": True,          # 是否使用 裁剪 tiny 模型
    "max_box_num": 6,          # 一幅图上最多有多少个目标
    "num_epochs": 100,
    "train_batch_size": 32,      # 对于完整 yolov3，每一批的训练样本不能太多，内存会炸掉；如果使用 tiny，可以适当大一些
    "use_gpu": False,
    "yolo_cfg": {
        "input_size": [3, 448, 448],    # 原版的边长大小为608，为了提高训练速度和预测速度，此处压缩为448
        "anchors": [7, 10, 12, 22, 24, 17, 22, 45, 46, 33, 43, 88, 85, 66, 115, 146, 275, 240],
        "anchor_mask": [[6, 7, 8], [3, 4, 5], [0, 1, 2]]
    },
    "yolo_tiny_cfg": {
        "input_size": [3, 224, 224],
        "anchors": [ 0,1,  0,2,  1,3,  2,4,  3,1,  4,1],
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
        "learning_rate": 0.001,
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
    file_list = os.path.join(train_parameters['data_dir'], train_parameters['train_list'])
    label_list = os.path.join(train_parameters['data_dir'], "label_list")
    print(file_list)
    print(label_list)
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
        
import codecs
import sys
import numpy as np
import time
#import paddle
#import paddle.fluid as fluid
import math
import functools

#from IPython.display import display
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from collections import namedtuple


init_train_parameters()
ues_tiny = train_parameters['use_tiny']
yolo_config = train_parameters['yolo_tiny_cfg'] if ues_tiny else train_parameters['yolo_cfg']

target_size = yolo_config['input_size']
anchors = yolo_config['anchors']
anchor_mask = yolo_config['anchor_mask']
label_dict = train_parameters['num_dict']
class_dim = train_parameters['class_dim']
print("label_dict:{} class dim:{}".format(label_dict, class_dim))
#place = fluid.CUDAPlace(0) if train_parameters['use_gpu'] else fluid.CPUPlace()
#exe = fluid.Executor(place)
#path = train_parameters['freeze_dir']
#print("luuuu,{}".format(path))
#[inference_program, feed_target_names, fetch_targets] = fluid.io.load_inference_model(dirname=path, executor=exe)
path = train_parameters['freeze_dir']
model_dir = path
pm_config1 = pm.PaddleMobileConfig()
pm_config1.precision = pm.PaddleMobileConfig.Precision.FP32######ok
pm_config1.device = pm.PaddleMobileConfig.Device.kFPGA######ok
pm_config1.model_dir = model_dir
predictor1 = pm.CreatePaddlePredictor(pm_config1)
pm_config1.thread_num = 2    

def draw_bbox_image(img, boxes, labels, save_name):
    """
    给图片画上外接矩形框
    :param img:
    :param boxes:
    :param save_name:
    :param labels
    :return:
    """

    img_width, img_height = img.size
    draw = ImageDraw.Draw(img)
    for box, label in zip(boxes, labels):
        print("label:",label_dict[int(label)])
        xmin, ymin, xmax, ymax = box[0], box[1], box[2], box[3]
        draw.rectangle((xmin, ymin, xmax, ymax), None, 'red')
        draw.text((xmin, ymin), label_dict[int(label)], (255, 255, 0))
    img.save(save_name)
    #display(img)


def resize_img(img, target_size):
    """
    保持比例的缩放图片
    :param img:
    :param target_size:
    :return:
    """
    img = img.resize(target_size[1:], Image.BILINEAR)
    return img


def read_image(img_path):
    """
    读取图片
    :param img_path:
    :return:
    """
    origin = Image.open(img_path)
    img = resize_img(origin, target_size)
    resized_img = img.copy()
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img = np.array(img).astype('float32').transpose((2, 0, 1))  # HWC to CHW
    img -= 127.5
    img *= 0.007843
    img = img[np.newaxis, :]
    return origin, img, resized_img


def infer(image_path):
    """
    预测，将结果保存到一副新的图片中
    :param image_path:
    :return:
    """
    origin, tensor_img, resized_img = read_image(image_path)
    input_w, input_h = origin.size[0], origin.size[1]
    image_shape = np.array([input_h, input_w], dtype='int32')
    # print("image shape high:{0}, width:{1}".format(input_h, input_w))
    t1 = time.time()
    '''batch_outputs = exe.run(inference_program,
                            feed={feed_target_names[0]: tensor_img,
                                  feed_target_names[1]: image_shape[np.newaxis, :]},
                            fetch_list=fetch_targets,
                            return_numpy=False)'''
    tensor = pm.PaddleTensor()
    tensor.dtype =pm.PaddleDType.FLOAT32
    tensor.shape  = (1,3,input_w,input_h)
    tensor.data = pm.PaddleBuf(tensor_img)
    paddle_data_feeds = [tensor]
        
    tensor_out = pm.PaddleTensor()
    tensor_out.dtype =pm.PaddleDType.FLOAT32
    tensor_out.shape  = ()##????????????????????????????????
    tensor_out.data = pm.PaddleBuf()
    batch_outputs = [tensor_out]  
    batch_outputs = predictor1.Run(paddle_data_feeds)
    
    period = time.time() - t1
    print("predict cost time:{0}".format("%2.2f sec" % period))
    bboxes = np.array(batch_outputs[0])
    #print(bboxes)

    if len(bboxes.shape) == 1 :
        print("No object found in {}".format(image_path))
        return
    labels = bboxes[:, 0].astype('int32')
    scores = bboxes[:, 1].astype('float32')
    boxes = bboxes[:, 2:].astype('float32')
    n_labels=[]
    n_boxes=[]

    for i in range(len(labels)):
        if(scores[i]>0.3):
            n_labels.append(labels[i])
            n_boxes.append(boxes[i])
    print("box:{}".format(n_boxes)) 
    print("label:{}".format(n_labels))
    last_dot_index = image_path.rfind('.')
    out_path = image_path[:last_dot_index]
    out_path = './1_result.jpg'
    #draw_bbox_image(origin, boxes, labels, out_path)
    draw_bbox_image(origin, n_boxes, n_labels, out_path)
    send_data='null'
    for i in range(len(n_labels)):
        send_data = label_dict[n_labels[i]]
    print("send_data:{}".format(send_data))

if __name__ == '__main__':
    cam = cv2.VideoCapture(2)
    while 1:
        #time.sleep(1)
        nowtime= time.time()
        print("solve main problem")
        ret,frame = cam.read()
        res=cv2.resize(frame,(224,224),interpolation=cv2.INTER_CUBIC)
        cv2.imwrite("1.jpg",res)
        image_path = "1.jpg"
        infer(image_path)
        print("************************************** rate:",1.0/(time.time()-nowtime))
