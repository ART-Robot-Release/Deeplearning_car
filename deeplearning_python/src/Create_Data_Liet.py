import json
import os
import numpy as np
from sys import argv
import getopt


#script, data_name, img_name = argv

path = os.path.split(os.path.realpath(__file__))[0]+"/.."
#script, vels = argv
opts,args = getopt.getopt(argv[1:],'-hH',['test_list=','train_list=','data_name=','img_name='])
#print(opts)

test_list = "test.list"
train_list = "train.list"
data_name = "data.npy"
img_name = "hsv_img"

#camera = "/dev/video0"

for opt_name,opt_value in opts:
    if opt_name in ('-h','-H'):
        print("python3 Create_Data_Liet.py  --test_list=%s   --train_list=%s  --data_name=%s  --img_name=%s"%(test_list , train_list , data_name , img_name))
        exit()

    if opt_name in ('--test_list'):
        test_list  = opt_value

    if opt_name in ('--train_list'):
        train_list = opt_value
        
    if opt_name in ('--data_name'):
        data_name = opt_value

    if opt_name in ('--img_name'):
        img_name = opt_value
        
def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
        print("----- new folder -----")
    else:
        print('----- there is this folder -----')

def create_data_list(data_name, img_name):
    with open( test_list, 'w') as f:
        pass
    with open(train_list, 'w') as f:
        pass

    #data = np.load(os.path.join(data_root_path, data_name))
    data = np.load( data_name)
    data = data.astype('float32')
    print('loading image：%s' % img_name)

    class_sum = 0
    #path = data_root_path + '/' + img_name

    #img_paths = os.listdir(path)
    img_paths = os.listdir(img_name)
    for img_path in img_paths:

        name_path = img_name + '/' + img_path
        index = int(img_path.split('.')[0])

        if not os.path.exists(data_root_path):
            os.makedirs(data_root_path)

        if class_sum % 10 == 0:
            with open( test_list, 'a') as f:
                f.write(name_path + "\t%d" % data[index] + "\n")
        else:
            with open(train_list, 'a') as f:
                f.write(name_path + "\t%d" % data[index] + "\n")
        class_sum += 1
    print('图像列表已生成')


if __name__ == '__main__':

    data_root_path = path+ '/data/'
    mkdir(data_root_path)
    test_list  = path + '/data/' + test_list
    train_list  = path + '/data/' + train_list
    data_name  = path + '/data/' + data_name
    img_name  = path + '/data/' + img_name
    
    
    create_data_list(data_name, img_name)

