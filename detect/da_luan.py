import random
 
def ReadFileDatas():
    FileNamelist = []
    file = open('train.txt','r+')
    for line in file:
        line=line.strip('\n') #删除每一行的\n
        FileNamelist.append(line)
    print('len ( FileNamelist ) = ' ,len(FileNamelist))
    file.close()
    return FileNamelist
 
def WriteDatasToFile(listInfo):
    file_handle=open('train_1.txt',mode='a')
    for idx in range(len(listInfo)):
        str = listInfo[idx]
        #查找最后一个 “_”的位置
        ndex = str.rfind('_')
        #print('ndex = ',ndex)
        #截取字符串
        str_houZhui = str[(ndex+1):]
        #print('str_houZhui = ',str_houZhui)
        str_Result = str  + '\n'           #+ str_houZhui+'\n'
        print(str_Result)
        file_handle.write(str_Result)
    file_handle.close()
 
if __name__ == "__main__":
    listFileInfo = ReadFileDatas()
    #打乱列表中的顺序
    random.shuffle(listFileInfo)
    WriteDatasToFile(listFileInfo)
