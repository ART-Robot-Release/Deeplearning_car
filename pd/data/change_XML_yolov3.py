from xml.etree.ElementTree import ElementTree,Element
import xml.etree.ElementTree as ET
import os


def mkdir(path):
    # 引入模块
    import os

    # 去除首位空格
    path=path.strip()
    # 去除尾部 \ 符号
    path=path.rstrip("\\")

    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists=os.path.exists(path)

    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path)

        print (path+' 创建成功')
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        print (path+' 目录已存在')
        return False

#读取名称文件
f = open("label_list")
names = []
while 1:
    line = f.readline()
    if not line:
        break
    line=line.replace('\n','')
    names.append(line)
print(names)
#查找目录下的xml文件
di_=os.listdir("./train/")
dir_list = []
for i in range(len(di_)):
        if di_[i].find('xml')!=-1:
            tmp_str = "./train/" + di_[i]
            dir_list.append(tmp_str)
#print(dir_list)
#保存目录
air_list=[]
msg_list=[]
for i in range(len(dir_list)):
    file_name=dir_list[i]
    x1=[]
    y1=[]
    x2=[]
    y2=[]
    tmp_name=[]
    try:
        tree = ET.parse(file_name)
    except IOError:
        exit(0)
    root = tree.getroot()
    #遍历文件所有的tag 为目标的值得标签
    for elem in root.iter('xmin'):
        x1.append(elem.text)
    for elem in root.iter('ymin'):
        y1.append(elem.text)
    for elem in root.iter('xmax'):
        x2.append(elem.text)
    for elem in root.iter('ymax'):
        y2.append(elem.text)
    #得到图片大小
    for elem in root.iter('width'):
        p_w=int(elem.text)
    for elem in root.iter('height'):
        p_h=int(elem.text)
    for elem in root.iter('name'):
        tmp_name.append(elem.text)
#    print(file_name)
#    print(x1,y1,x2,y2)
#    print(tmp_name)
#    print("-----------------------------")
#{"value":"crossing","coordinate":[[10,80],[407,196]]}
    write_data =''
    #目标中心
    for i in range(len(tmp_name)):	
        tmp_write_data = '{'
        tmp_write_data = tmp_write_data + "\"value\":\"{}\",\"coordinate\":[[{},{}],[{},{}]]".format(tmp_name[i],x1[i],y1[i],x2[i],y2[i])
        tmp_write_data = tmp_write_data + '}'
        if i==0 :
            write_data = write_data + tmp_write_data
        else :
            write_data = write_data + '\t' +tmp_write_data
        
    msg_list.append(write_data)
    print(write_data)
    write_name = file_name.replace('xml','jpg')
    air_list.append(write_name)

    #w_file = open(write_name,'w')
    #w_file.write(write_data)

w_file = open("./train.txt",'w')
count = 0;
for i in air_list:
    #cwd=os.getcwd()
    tmp = i.replace("./train","data/train")
    tmp=  tmp + '\t' + msg_list[count] + '\n'
    #i = i + "\n"
    print(tmp)
    w_file.write(tmp)
    count=count+1
