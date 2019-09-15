# -*- coding: UTF-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Ui_userInteractWin import Ui_Form
from userPayWin import UserPayWin
from itemInfo import ItemInfo
import utils
import app as detect
import cv2
import sys, time
import numpy as np
import serial

'''
reload(sys)
sys.setdefaultencoding('utf8')
'''

tempImgPath = 'tempImg.jpg'
weight_num = 0.0
itemName = ''
itemSimprice = 0.0 # defined add yuan
#simPrice = 0.0 # defined num
toPrice = 0.0
label = 0

class MainInteractInterface(QWidget, Ui_Form):
    guideInfo = pyqtSignal(str) # 发送需要让使用者知道的状态信息

    def __init__(self, parentWidget=None):
        super(MainInteractInterface, self).__init__(parentWidget)
        self.setupUi(parentWidget)
        rknn = utils.load_model()

        self.guideInfoLabel.setWordWrap(True)
        self.itemSelectbtn.setEnabled(False)

        self.itemGroupBoxNum = 0
        self.itemInfodict = {1: None, 2: None, 3: None, 4: None, 5: None, 6: None} # 字典初值类型一旦确定就会沿用

        self.cap = cv2.VideoCapture(0)
        self.timer_camera_serial = QTimer(self)
        self.timer_item_thread = QTimer(self)
        self.timer_checkConfirmBtn_thread = QTimer(self)
        self.itemRecogThread = ItemRecogThread(rknn)
        self.detectSerialisOpened() # 串口初始化
        self.slot_init() # 槽函数初始化
        self.function_init()

    def show_camera(self):
        flag, image = self.cap.read()
        #print(image.shape)
        if flag == False:
            self.guideInfo.emit('请检查相机是否连接正确')
        else: # 只开启一次计时器
            #show = image[65:415, 85:555] # 裁去边框，增加识别准确率
            # cv2.imwrite(tempImgPath, show)
            # 将拍摄的图片展示到label上
            #show = cv2.resize(show, (620, 520))# 避免显示出问题
            imgInfo = image.shape
            height = imgInfo[0] # 480
            width = imgInfo[1] # 640
            matRotate = cv2.getRotationMatrix2D((height*0.5,width*0.5), 90, 1) # 旋转矩阵
            show_rotate = cv2.warpAffine(image, matRotate, (height, width)) # 旋转api 高度640， 宽度480
            img_save = show_rotate[100:400, 0:300]
            cv2.imwrite(tempImgPath, img_save) # 保存拍摄的图片，供识别使用

            img_show = show_rotate[100:400, 0:400]
            show = cv2.cvtColor(img_show, cv2.COLOR_BGR2RGB)
            showImage = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
            self.cameraImg.setScaledContents(True)
            self.cameraImg.setPixmap(QPixmap.fromImage(showImage))

    def function_init(self):
        self.timer_camera_serial.start(30)
        self.timer_checkConfirmBtn_thread.start(100)
        self.timer_item_thread.start(700)

    def slot_init(self): 
        self.timer_camera_serial.timeout.connect(self.show_camera) # 照片刷新和串口接收数据的频率
        self.timer_item_thread.timeout.connect(self.item_recog) # 识别物体的频率
        self.timer_checkConfirmBtn_thread.timeout.connect(self.checkConfirmBtn) # 当选择了物品清单时支付按钮才能被按下
        self.timer_camera_serial.timeout.connect(self.serial_read)
        self.itemRecogThread.sinOut.connect(self.show_item_info) # 在主线程显示物品名称及单价
        self.guideInfo.connect(self.sendGuideInfo) # 打印提示信息
        self.serialThread.sinOut.connect(self.show_item_weight) # 在主线程显示物品重量
        self.itemSelectbtn.clicked.connect(self.addItemInfo) # 顾客确定选择当前商品

        # 取消物品选择按钮槽函数初始化
        self.cancelbtn1.clicked.connect(self.cancelBtn1Funcion)
        self.cancelbtn2.clicked.connect(self.cancelBtn2Funcion)
        self.cancelbtn3.clicked.connect(self.cancelBtn3Funcion)
        self.cancelbtn4.clicked.connect(self.cancelBtn4Funcion)
        self.cancelbtn5.clicked.connect(self.cancelBtn5Funcion)
        self.cancelbtn6.clicked.connect(self.cancelBtn6Funcion)

        self.confirmedPaybtn.clicked.connect(self.showPayItemList) # 用户支付界面
        self.confirmedPaybtn.setEnabled(False)
        self.exit2initial.clicked.connect(self.closeWin)

    def closeWin(self):
        print('Exit Form by del')
        if self.cap.isOpened():
            self.cap.release()
        if self.timer_camera_serial.isActive():
            self.timer_camera_serial.stop()
        if self.timer_item_thread.isActive():
            self.timer_item_thread.stop()
        if self.timer_checkConfirmBtn_thread.isActive():
            self.timer_checkConfirmBtn_thread.stop()
        if self.mySerial.is_open:
            self.mySerial.close()
        self.totalPrice.clear()
        time.sleep(1.5)
        self.form.close()


    def checkConfirmBtn(self):
        checkConfirmBtnThread = CheckConfirmBtnThread(self.confirmedPaybtn, self.itemInfodict)
        checkConfirmBtnThread.start()

    def item_recog(self):
        self.itemRecogThread.start()
    
    def serial_read(self):
        self.serialThread.start()

    def show_item_info(self, name, simprice, label_):
        print('name:', name )
        global itemName
        global toPrice
        global itemSimprice
        global label
        self.guideInfo.emit('请将水果依次放入托盘上，添加到预购清单请按“确认选择”按钮，购买请按“确认支付”按钮')
        if name == '空盘':
            itemSimprice = 0
            self.objName.setText(' ')
            self.simPrice.setText(' ')
            self.totalPrice.setText(' ')
            self.itemSelectbtn.setEnabled(False)
        else:
            itemSimprice = float('%.2f' %simprice)
            itemName = name
            label = label_

            self.objName.setText(name)
            self.simPrice.setText(str(itemSimprice) + '元')
            toPrice = itemSimprice * weight_num
            toPrice = float('%.2f' % toPrice)
            totalPrice_s = str(toPrice) + '元'
            self.totalPrice.setText(totalPrice_s)
            self.itemSelectbtn.setEnabled(True)

    def show_item_weight(self, weight):
        self.objWeight.setText(weight)
        global itemSimprice
        global toPrice
        if itemSimprice != 0:
            toPrice = itemSimprice * weight_num
            toPrice = float('%.2f' % toPrice)
            totalprice_s = str(toPrice) + '元'
            self.totalPrice.setText(totalprice_s)

    def showPayItemList(self):
        self.timer_item_thread.stop()
        self.timer_camera_serial.stop() 
        self.timer_checkConfirmBtn_thread.stop()
        time.sleep(1)
        print('暂停识别')
        #self.guideInfoLabel.clear()
        self.guideInfoLabel.setText('正在结算，请稍后...')
        userPayWin = QDialog()
        # print(self.itemInfodict[1].getTotalInfo())
        UserPayWin(parentWidget=userPayWin, item_info_dict=self.itemInfodict) # 在userPayWin上初始化控件
        userPayWin.setWindowModality(Qt.ApplicationModal)
        userPayWin.show()
        userPayWin.exec_() # 循环执行userPayWin
        
        self.itemInfoGroupbox1.setVisible(False)
        self.itemInfoGroupbox2.setVisible(False)
        self.itemInfoGroupbox3.setVisible(False)
        self.itemInfoGroupbox4.setVisible(False)
        self.itemInfoGroupbox5.setVisible(False)
        self.itemInfoGroupbox6.setVisible(False)

        self.itemInfodict[1] = None
        self.itemInfodict[2] = None
        self.itemInfodict[3] = None
        self.itemInfodict[4] = None
        self.itemInfodict[5] = None
        self.itemInfodict[6] = None
        self.timer_item_thread.start(700)
        self.timer_camera_serial.start(30)
        self.timer_checkConfirmBtn_thread.start(100)
        print('恢复识别')

    def addItemInfo(self): # 将顾客选择的水果集中显示
        itemInfo = ItemInfo(itemName, weight_num, itemSimprice, toPrice, label)
        if not self.itemInfoGroupbox1.isVisible():
            self.itemInfoGroupbox1.setVisible(True)
            self.item_name1.setText('名称:'+itemName)
            self.item_simprice1.setText('单价:'+str(itemSimprice)+'元') # 文本控件追加字符
            self.item_toprice1.setText('总价:'+str(toPrice)+'元')
            self.item_weight1.setText('重量:'+str(weight_num)+'kg')
            self.itemInfoGroupbox1.setTitle(utils.category_confirm(label)) # 设置显示的物品类别

            self.itemInfodict[1] = itemInfo # 将水果放入列表，方便生成表单
        elif not self.itemInfoGroupbox2.isVisible():
            self.itemInfoGroupbox2.setVisible(True)
            self.item_name2.setText('名称:'+itemName)
            self.item_simprice2.setText('单价:'+str(itemSimprice)+'元')
            self.item_toprice2.setText('总价:'+str(toPrice)+'元')
            self.item_weight2.setText('重量:'+str(weight_num)+'kg')
            self.itemInfoGroupbox2.setTitle(utils.category_confirm(label)) # 设置显示的物品类别

            self.itemInfodict[2] = itemInfo # 将水果放入列表，方便生成表单
        elif not self.itemInfoGroupbox3.isVisible():
            self.itemInfoGroupbox3.setVisible(True)
            self.item_name3.setText('名称:'+itemName)
            self.item_simprice3.setText('单价:'+str(itemSimprice)+'元')
            self.item_toprice3.setText('总价:'+str(toPrice)+'元')
            self.item_weight3.setText('重量:'+str(weight_num)+'kg')
            self.itemInfoGroupbox3.setTitle(utils.category_confirm(label)) # 设置显示的物品类别

            self.itemInfodict[3] = itemInfo # 将水果放入列表，方便生成表单
        elif not self.itemInfoGroupbox4.isVisible():
            self.itemInfoGroupbox4.setVisible(True)
            self.item_name4.setText('名称:'+itemName)
            self.item_simprice4.setText('单价:'+str(itemSimprice)+'元')
            self.item_toprice4.setText('总价:'+str(toPrice)+'元')
            self.item_weight4.setText('重量:'+str(weight_num)+'kg')
            self.itemInfoGroupbox4.setTitle(utils.category_confirm(label)) # 设置显示的物品类别

            self.itemInfodict[4] = itemInfo # 将水果放入列表，方便生成表单
        elif not self.itemInfoGroupbox5.isVisible():
            self.itemInfoGroupbox5.setVisible(True)
            self.item_name5.setText('名称:'+itemName)
            self.item_simprice5.setText('单价:'+str(itemSimprice)+'元')
            self.item_toprice5.setText('总价:'+str(toPrice)+'元')
            self.item_weight5.setText('重量:'+str(weight_num)+'kg')
            self.itemInfoGroupbox5.setTitle(utils.category_confirm(label)) # 设置显示的物品类别

            self.itemInfodict[5] = itemInfo # 将水果放入列表，方便生成表单
        elif not self.itemInfoGroupbox6.isVisible():
            self.itemInfoGroupbox6.setVisible(True)
            self.item_name6.setText('名称:'+itemName)
            self.item_simprice6.setText('单价:'+str(itemSimprice)+'元')
            self.item_toprice6.setText('总价:'+str(toPrice)+'元')
            self.item_weight6.setText('重量:'+str(weight_num)+'kg')
            self.itemInfoGroupbox6.setTitle(utils.category_confirm(label)) # 设置显示的物品类别

            self.itemInfodict[6] = itemInfo # 将水果放入列表，方便生成表单

    def cancelBtn1Funcion(self):
        self.itemInfoGroupbox1.setVisible(False)
        self.itemInfodict[1] = None
    
    def cancelBtn2Funcion(self):
        self.itemInfoGroupbox2.setVisible(False)
        self.itemInfodict[2] = None

    def cancelBtn3Funcion(self):
        self.itemInfoGroupbox3.setVisible(False)
        self.itemInfodict[3] = None

    def cancelBtn4Funcion(self):
        self.itemInfoGroupbox4.setVisible(False)
        self.itemInfodict[4] = None

    def cancelBtn5Funcion(self):
        self.itemInfoGroupbox5.setVisible(False)
        self.itemInfodict[5] = None

    def cancelBtn6Funcion(self):
        self.itemInfoGroupbox6.setVisible(False)
        self.itemInfodict[6] = None

    def sendGuideInfo(self, text):
        self.guideInfoLabel.setText(str(text))
        

    def detectSerialisOpened(self): # 检测并打开串口
        self.mySerial = serial.Serial('/dev/ttyS4', 9600, timeout = 60)
        #self.serial.open()
        if self.mySerial.is_open:
            self.serialThread = SerialThread(self.mySerial)
            print('serial open success')
        else:
            self.guideInfo.emit('串口打开失败')

class ItemRecogThread(QThread):
    sinOut = pyqtSignal(str, float, int)

    def __init__(self, rknn):
        super(ItemRecogThread, self).__init__()
        global rknn_
        rknn_ = rknn

    def __del__(self):
        self.wait()

    def run(self):
        result = detect.application(tempImgPath, rknn_)
        global simprice 
        simprice = result[1]
        self.sinOut.emit(str(result[0]), result[1], result[2])

class SerialThread(QThread):
    sinOut = pyqtSignal(str)

    def __init__(self, mySerial):
        super(SerialThread, self).__init__()
        self.mserial = mySerial

    def __del__(self):
        self.wait()

    def run(self):
        data = self.mserial.read(16)
        '''
        #print('origin_weight_data:', data)
        datas = data[3:15]
        datas = datas.split(',')
        weight_origin = datas[0]
        print('disposed_weight_data:', weight_origin)
        '''
        #data = data.decode('utf-8')
        data = str(data)
        #print('weight:', data)
        str_weight_list = []
        for i in data:
            if str(i).isdigit():
                str_weight_list.append(str(i))
            if str(i) is '.':
                str_weight_list.append(str(i))
            if str(i) is ',':
                break
        str_weight = ''.join(str_weight_list)
        # print(str_weight)
        global weight_num 
        weight_num = float(str_weight)
        weight_num = float('%.2f' %weight_num)
        weight = str(weight_num) + 'kg'
        self.sinOut.emit(weight)

class CheckConfirmBtnThread(QThread):

    def __init__(self, confirmBtn, itemInfoDict):
        super(CheckConfirmBtnThread, self).__init__()
        self.confirmBtn = confirmBtn
        self.itemInfoDict = itemInfoDict

    def __del__(self):
        self.wait()

    def run(self):
        num = 0
        for value in self.itemInfoDict.values():
            if value != None:
                num +=1
        if num == 0:
            self.confirmBtn.setEnabled(False)
        else:
            self.confirmBtn.setEnabled(True)







