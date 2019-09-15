# -*- coding: UTF-8 -*-
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QWidget
from PyQt5 import QtWidgets
from Ui_initialWin import Ui_MainWindow
from callUserInterfaceWin import MainInteractInterface
import sys

class InitalWin(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(InitalWin, self).__init__()
        self.setupUi(self)

        self.detectpayButton.clicked.connect(self.openUserInterfaceWin)

    def openUserInterfaceWin(self):
        self.hide()
        userInterfaceWin = QDialog()
        MainInteractInterface(userInterfaceWin) # 在userInterfaceWin上初始化控件
        userInterfaceWin.show()
        userInterfaceWin.exec_() # 循环执行userInterfaceWIn
        self.show() # 关闭userInterfaceWin之后开启主界面

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = InitalWin()
    myWin.show()
    sys.exit(app.exec_())
