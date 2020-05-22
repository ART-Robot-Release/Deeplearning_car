# -*- coding:utf-8 -*-
"""
python3 txt2npy.py data.npy

"""
import os
from ctypes import *
import struct, array
from fcntl import ioctl
import cv2
import numpy as np
import time
from sys import argv

#script, data_name = argv

data_name ="data.npy"
angledata = []
file = open("data.txt")

for line in file.readlines():
    line=line.strip('\n')
    ##注意赋值给angle
    
    angle = int(line)
    ##获取角度angle；逐一调用
    angledata.append(angle)
    print(angle)
    data = np.array(angledata)
    data_path = os.path.join(os.getcwd(), data_name)
    np.save(data_path, data)
file.close() 
