# -*- coding: utf-8 -*-
from xml.etree.ElementTree import ElementTree,Element
import xml.etree.ElementTree as ET
import cv2 
import numpy as np


m=0
while m <= 550:   
    tree = ET.parse('/home/deep/12121/data/000/{}.xml'.format(m))
    #tree = ET.parse('D:\python\venv1\output.xml')
    root = tree.getroot()

    #遍历文件所有的tag 为目标的值得标签
    '''for elem in root.iter('xmin'):
        new_elem=(int(elem.text)/2+int(elem.text)%2)
        elem.text = str(new_elem)
    for elem in root.iter('ymin'):
        new_elem=(int(elem.text)/2+int(elem.text)%2)
        elem.text = str(new_elem)
    for elem in root.iter('xmax'):
        new_elem=(int(elem.text)/2+int(elem.text)%2)
        elem.text = str(new_elem)
    for elem in root.iter('ymax'):
        new_elem=(int(elem.text)/2+int(elem.text)%2)
        elem.text = str(new_elem)
    for elem in root.iter('width'):
        new_elem=800
        elem.text = str(new_elem)
    for elem in root.iter('height'):
        new_elem=800
        elem.text = str(new_elem)'''
    for elem in root.iter('name'):
        elem.text = "limit_10"
    for elem in root.iter('name'): 
        print(str(elem.text))
        #new_elem="limit_10"     
    tree.write('/home/deep/12121/data/001/{}.xml'.format(m))
    print(m)
    m +=1
'''m=0
while m <= 2000:  
    img0 = np.zeros((500,500,3),dtype=np.uint8)
    img0[:,:]=[255,255,255]
    img = cv2.imread('/home/deep/桌面/new_img/{}.jpg'.format(m))
    i = 0
    while i<420:
        j = 0
        while j<240:
            img0[j,i]=img[j,i]
            j +=1
        i+=1
    cv2.imwrite('/home/deep/桌面/image800_800/{}.jpg'.format(m),img0)
    print(m)
    m+=1
'''
