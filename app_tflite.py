# -*- coding: UTF-8 -*-
import os
import cv2
import numpy as np
import time
import labels

import tensorflow as tf

#model_path = "./model/quantize_frozen_graph.tflite"
model_path = "./mobilenet_v2_1.4_224.tflite"

def load_model(inputData):
    # Load TFLite model and allocate tensors.
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    # Get input and output tensors.
    input_details = interpreter.get_input_details()
    print(str(input_details))
    output_details = interpreter.get_output_details()
    print(str(output_details))

    model_interpreter_time = 0
    start_time = time.time()
    # 填装数据
    model_interpreter_start_time = time.time()
    interpreter.set_tensor(input_details[0]['index'], inputData)

    # 注意注意，我要调用模型了
    interpreter.invoke()
    result = interpreter.get_tensor(output_details[0]['index'])
    model_interpreter_time += time.time() - model_interpreter_start_time
    
    # 出来的结果去掉没用的维度
    print('result:{}'.format(result))
    #print('result:{}'.format(sess.run(output, feed_dict={newInput_X: image_np_expanded})))
        
    # 输出结果是长度为10（对应0-9）的一维数据，最大值的下标就是预测的数字
    print('result:{}'.format( (np.where(result==np.max(result)))[0][0]  ))
    used_time = time.time() - start_time
    print('used_time:{}'.format(used_time))
    print('model_interpreter_time:{}'.format(model_interpreter_time))
    return 1

def pre_pic(picName):
    img = cv2.imread(picName)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    reIm = cv2.resize(img, (224, 224))
    im_arr = np.array(reIm)
    im_arr = im_arr.reshape([1, 224, 224, 3])
    img = im_arr.astype(np.float32)
    img = np.multiply(img, 1.0/128.0) -1

    return img  #img

def application(imgPath):
    name_label_price = []
    testPicArr = pre_pic(imgPath)
    preValue = load_model(testPicArr)
    print('preValue:', preValue)
    name_label_price.append(labels.labels[int(preValue)])
    name_label_price.append(labels.prices[int(preValue)])
    name_label_price.append(preValue)
    return name_label_price

