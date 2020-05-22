ssh  deep@192.168.5.101  
password:artrobot  

0 删除里面数据  
cd ~/ART_Deeplearning_car/src  
sudo rm -r ./data   #删除数据  
sudo rm -r ./model  #删除模型   

1  采集数据   
cd ~/ART_Deeplearning_car/src   
python3 Data_Coll.py   
or:   python3 Data_Coll.py --vels=1560 --output=data --serial=/dev/ttyUSB0 --camera=/dev/video0  --save_name=img   
##生成：../data/img   ../data/data.npy   

2  处理数据   
cd ~/ART_Deeplearning_car/src   
python3 Img_Handle.py     
or:   python3 Img_Handle.py  --img_path=img   --save_path=hsv_img   
##生成：../data/hsv_img   

3  生成训练和测试序列   
cd ~/ART_Deeplearning_car/src   
python3 Create_Data_Liet.py    
or:   python3 Create_Data_Liet.py  --test_list=test.list   --train_list=train.list  --data_name=data.npy  --img_name=hsv_img   
##生成：../data/train.list     ../data/test.list    

4  训练数据   
cd ~/ART_Deeplearning_car/src  
python3 Train_Model.py     
or:   python3 Train_Model.py  --test_list=test.list   --train_list=train.list  --save_path=model_infer   
## 生成训练模型  ./model/model_infer

5  自主移动   
cd ~/ART_Deeplearning_car/src  
cd ~/paddle_py_ok/src   
python3 Auto_Driver.py    
or:   python3 Auto_Driver.py --save_path=model_infer  --vels=1560 --camera=/dev/video0   
## 小车自主移动  
   
