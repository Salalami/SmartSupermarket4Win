# -*- coding: UTF-8 -*-
import labels, cv2
import tensorflow as tf
import numpy as np
from tensorflow.contrib import slim
import datetime
import time

checkpoint = 'trained_models'

def restore_model(testPicArr, rknn):
    output = rknn.inference(inputs=[testPicArr], data_type='float32')
    print('output:', output)
    data = output[0][0]
    print('data:', data)
    preValue = np.argmax(data)
    return preValue

def pre_pic(picName):
    img = cv2.imread(picName)
    #try:
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #except:
    #img = cv2.imread('tempImgd.jpg')
    #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    reIm = cv2.resize(img, (224, 224))
    im_arr = np.array(reIm)
    im_arr = im_arr.reshape([1, 224, 224, 3])
    img = im_arr.astype(np.float32)
    img = np.multiply(img, 1.0/128.0) -1

    return img  #img

def application(imgPath, rknn):
    t1 = datetime.datetime.now().microsecond
    t3 = time.mktime(datetime.datetime.now().timetuple())
    name_label_price = []
    testPicArr = pre_pic(imgPath)
    preValue = restore_model(testPicArr, rknn)
    print('preValue:', preValue)
    name_label_price.append(labels.labels[int(preValue)])
    name_label_price.append(labels.prices[int(preValue)])
    name_label_price.append(preValue)
    t2 = datetime.datetime.now().microsecond
    t4 = time.mktime(datetime.datetime.now().timetuple())
    strTime = 'function time use:%dms' % ((t4-t3)*1000 + (t2-t1)/1000) 
    print(strTime) # max 120ms
    return name_label_price