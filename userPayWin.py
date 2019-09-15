from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QWidget, QMessageBox
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, QThread, QCoreApplication, Qt
from Ui_userPayWin import Ui_Dialog
import sys, utils
from alipay import AliPay
import qrcode, time, threading, sched

alipay_public_key_string = open("alipay_public_key_string.txt").read()
app_private_key_string = open("app_private_key_string.txt").read()
APP_ID = '2016093000628067'

PRECREATE_ORDER_FAIL = 10
PRECREATE_ORDER_SUCCESS = 20
PERCHASE_COMPLETEED = 30
PERCHASE_CANCELED = 40
PERCHASE_CANCELED_BY_BTN = 50

exit_flag = 1

class UserPayWin(QDialog, Ui_Dialog):
    sinOutExit = pyqtSignal()

    def __init__(self, item_info_dict, parentWidget=None):
        super(UserPayWin, self).__init__(parentWidget)
        self.setupUi(parentWidget)
        self.dialog.setWindowFlags(Qt.CustomizeWindowHint)
        self.cancelPaybtn.clicked.connect(self.queryDialog)
        self.qrcode.setScaledContents(True)
        self.sinOutExit.connect(self.disposeExitSignal)
        
        toPrice = 0.0
        for value in item_info_dict.values():
            if value != None:
                print(value.getTotalInfo())
                self.displayInfo(value)
                toPrice = toPrice + value.getToPrice()
                toPrice = float('%.2f' % toPrice)
                print('toPrice', toPrice)
        self.ToPrice.setText('总计: ' +str(toPrice)+ '元')
        self.myAlipay = AliPayUtil(app_private_key_string, alipay_public_key_string, self.helpInfo)
        subject = '购买水果付款'
        self.out_trade_no = int(time.time())
        result1 = self.myAlipay.preCreateOrder(subject, self.out_trade_no, toPrice) # 预创建订单
        if result1 == PRECREATE_ORDER_SUCCESS:
            self.qrcode.setPixmap(QPixmap('qr_ali.png'))
            self.alipayThread = QueryPaymentInfoThread(self.myAlipay, self.out_trade_no, 120)# 查询订单支付状态
            #self.checkFlagThread = CheckFlagThread() # 检查标志信号
            # 初始化槽函数
            self.alipayThread.sinOut.connect(self.show_help_info)
            #self.alipayThread.sinOutExit.connect(self.disposeExitSignal)
            #self.checkFlagThread.sinOut.connect(self.disposeExitSignal)
            self.alipayThread.finished.connect(self.disposeExitSignal)
            self.alipayThread.start()
            #self.checkFlagThread.start()
            #time.sleep(2) # 阻塞线程一会，让UI加载好
        elif result1 == PRECREATE_ORDER_FAIL:
            self.cancelPaybtn.setEnabled(False)
            s = threading.Timer(5, self.disposeExitSignal) # 延时函数，界面初始化完成时再关闭
            s.start()

    def disposeExitSignal(self):
        print('关闭付款界面')
        self.dialog.close()
    
    def show_help_info(self, info):
        self.helpInfo.clear()
        self.helpInfo.setText(str(info))

    def queryDialog(self):
        reply = QMessageBox.warning(self, "警告", '确定放弃购买？', QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            #global exit_flag
            #global exit_check_thread_flag
            #exit_check_thread_flag = 0
            global exit_flag
            exit_flag = 0
            #time.sleep(2)
            self.close()

    def displayInfo(self, itemInfo):
        itemName, itemSimprice, toPrice, weight_num, category = itemInfo.getTotalInfo() 
        if self.itemInfoGroupbox1.isHidden():
            self.itemInfoGroupbox1.setHidden(False)
            self.item_name1.setText('名称:'+itemName)
            self.item_simprice1.setText('单价:'+str(itemSimprice)+'元')
            self.item_toprice1.setText('总价:'+str(toPrice)+'元')
            self.item_weight1.setText('重量:'+str(weight_num)+'kg')
            self.itemInfoGroupbox1.setTitle(utils.category_confirm(category)) # 设置显示的物品类别

        elif self.itemInfoGroupbox1_2.isHidden():
            self.itemInfoGroupbox1_2.setHidden(False)
            self.item_name1_2.setText('名称:'+itemName)
            self.item_simprice1_2.setText('单价:'+str(itemSimprice)+'元')
            self.item_toprice1_2.setText('总价:'+str(toPrice)+'元')
            self.item_weight1_2.setText('重量:'+str(weight_num)+'kg')
            self.itemInfoGroupbox1_2.setTitle(utils.category_confirm(category)) # 设置显示的物品类别

        elif self.itemInfoGroupbox1_3.isHidden():
            self.itemInfoGroupbox1_3.setHidden(False)
            self.item_name1_3.setText('名称:'+itemName)
            self.item_simprice1_3.setText('单价:'+str(itemSimprice)+'元')
            self.item_toprice1_3.setText('总价:'+str(toPrice)+'元')
            self.item_weight1_3.setText('重量:'+str(weight_num)+'kg')
            self.itemInfoGroupbox1_3.setTitle(utils.category_confirm(category)) # 设置显示的物品类别

        elif self.itemInfoGroupbox1_4.isHidden():
            self.itemInfoGroupbox1_4.setHidden(False)
            self.item_name1_4.setText('名称:'+itemName)
            self.item_simprice1_4.setText('单价:'+str(itemSimprice)+'元')
            self.item_toprice1_4.setText('总价:'+str(toPrice)+'元')
            self.item_weight1_4.setText('重量:'+str(weight_num)+'kg')
            self.itemInfoGroupbox1_4.setTitle(utils.category_confirm(category)) # 设置显示的物品类别

        elif self.itemInfoGroupbox1_5.isHidden():
            self.itemInfoGroupbox1_5.setHidden(False)
            self.item_name1_5.setText('名称:'+itemName)
            self.item_simprice1_5.setText('单价:'+str(itemSimprice)+'元')
            self.item_toprice1_5.setText('总价:'+str(toPrice)+'元')
            self.item_weight1_5.setText('重量:'+str(weight_num)+'kg')
            self.itemInfoGroupbox1_5.setTitle(utils.category_confirm(category)) # 设置显示的物品类别

        elif self.itemInfoGroupbox1_6.isHidden():
            self.itemInfoGroupbox1_6.setHidden(False)
            self.item_name1_6.setText('名称:'+itemName)
            self.item_simprice1_6.setText('单价:'+str(itemSimprice)+'元')
            self.item_toprice1_6.setText('总价:'+str(toPrice)+'元')
            self.item_weight1_6.setText('重量:'+str(weight_num)+'kg')
            self.itemInfoGroupbox1_6.setTitle(utils.category_confirm(category)) # 设置显示的物品类别

class AliPayUtil: # 支付宝工具类

    def __init__(self, app_private_key_string_, alipay_public_key_string_, helpInfo):
        self.alipay = AliPay(
            appid=APP_ID,
            app_notify_url=None,
            app_private_key_string=app_private_key_string_,
            alipay_public_key_string=alipay_public_key_string_,
            sign_type='RSA2',
            debug=True
        )
        self.helpInfo = helpInfo

    def preCreateOrder(self, subject:'order_desc' , out_trade_no:int, total_amount:(float,'eg:0.01')):    
        '''    创建预付订单    
        :return None：表示预付订单创建失败  [或]  code_url：二维码url
        '''
        result = self.alipay.api_alipay_trade_precreate(
            subject=subject, # 商品名
            out_trade_no=out_trade_no,# 交易订单号，不可重复
            total_amount=total_amount)
        print('返回值：',result)
        msg = result.get('msg')
        if msg == 'Business Failed':
            print('预创建订单失败')
            self.helpInfo.clear()
            self.helpInfo.setText("订单创建失败，5s后窗口关闭")
            return PRECREATE_ORDER_FAIL
        elif msg == 'Success':
            code_url = result.get('qr_code')
            self.get_qr_code(code_url)
            return PRECREATE_ORDER_SUCCESS

    def get_qr_code(self, code_url):
        '''
        生成二维码
        ：return None
        '''
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4
        )
        qr.add_data(code_url) # 二维码所包含信息
        img = qr.make_image()
        img.save('qr_ali.png')
        print('二维码保存成功')

    def query_order(self, out_trade_no_:int, cancel_time:int and 'secs'):
        '''
        :param out_trade_no: 商户订单号
        :return: None
        '''
        print('预付订单已创建,请在%s秒内扫码支付,过期订单将被取消！'% cancel_time)
        # 检查订单状态
        _time = 0
        global exit_flag
        #print("check flag:", exit_check_thread_flag)
        for i in range(int(cancel_time / 2) + 10):
            if exit_flag == 0: # 按钮退出时结束线程
                exit_flag = 1
                return self.cancel_order(out_trade_no_, btnControl=True)
            # 每2s检查一次，共检查60次
            time.sleep(2)

            result = self.alipay.api_alipay_trade_query(out_trade_no=out_trade_no_)
            if result.get('trade_status', '') == "TRADE_SUCCESS":
                print('订单已支付')
                print('订单查询返回值：',result)
                return PERCHASE_COMPLETEED

            _time +=2
            print('accumulate time:', _time)
            if _time >= cancel_time:
                print('取消订单')
                return self.cancel_order(out_trade_no_, cancel_time)

    def cancel_order(self, out_trade_no_:int, cancel_time=None, btnControl=None): # 2参数对应不同的调用方式
        '''
        撤销订单
        :param cancel_time: 撤销前的等待时间(若未支付)，撤销后在商家中心-交易下的交易状态显示为"关闭"
        :return:
        '''
        result = self.alipay.api_alipay_trade_cancel(out_trade_no=out_trade_no_)
        print("取消订单result:", result)
        resp_state = result.get('msg')
        
        if resp_state == 'Success':
            if cancel_time:
                print("%s秒内未支付订单，订单已被取消！" % cancel_time)
                return PERCHASE_CANCELED
            elif btnControl:
                return PERCHASE_CANCELED_BY_BTN
        else:
            return 0

class QueryPaymentInfoThread(QThread):
    sinOut = pyqtSignal(str)
    #sinOutExit = pyqtSignal()

    def __init__(self, myAlipay, out_trade_no, query_time):
        super(QueryPaymentInfoThread, self).__init__()
        self.myalipay = myAlipay
        self.out_trade_no = out_trade_no
        self.query_time = query_time
    
    def run(self):
        print('开始查询订单状态')
        #global exit_flag
        result = self.myalipay.query_order(self.out_trade_no, self.query_time)
        if result == PERCHASE_CANCELED:
            self.sinOut.emit('购买超时，订单已取消！')
            time.sleep(3)
            #exit_flag = 0
            #self.sinOutExit.emit()
            
        elif result == PERCHASE_COMPLETEED:
            self.sinOut.emit('购买成功！')
            time.sleep(3)
            #self.sinOutExit.emit()
            #exit_flag = 0
        elif result == PERCHASE_CANCELED_BY_BTN:
            self.sinOut.emit('取消成功！')
            time.sleep(1)
            #self.sinOutExit.emit()





