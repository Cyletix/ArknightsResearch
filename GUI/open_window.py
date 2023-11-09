'''
Description: 文件描述
Author: Cyletix
Date: 2022-01-07 00:28:22
LastEditTime: 2022-01-07 00:28:22
FilePath: \ArknightsResearch\open_window.py
'''
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog
class window(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(0, 0, 391, 241))
        self.groupBox.setObjectName("groupBox")
        self.textEdit = QtWidgets.QTextEdit(self.groupBox)
        self.textEdit.setGeometry(QtCore.QRect(20, 50, 351, 181))
        self.textEdit.setObjectName("textEdit")
        self.comboBox = QtWidgets.QComboBox(self.groupBox)
        self.comboBox.setGeometry(QtCore.QRect(100, 20, 91, 20))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(30, 20, 61, 21))
        self.label.setObjectName("label")
        self.queryBtn = QtWidgets.QPushButton(Dialog)
        self.queryBtn.setGeometry(QtCore.QRect(40, 250, 75, 23))
        self.queryBtn.setMaximumSize(QtCore.QSize(75, 16777215))
        self.queryBtn.setObjectName("queryBtn")
        self.clearBtn = QtWidgets.QPushButton(Dialog)
        self.clearBtn.setGeometry(QtCore.QRect(250, 250, 75, 23))
        self.clearBtn.setMaximumSize(QtCore.QSize(75, 16777215))
        self.clearBtn.setObjectName("clearBtn")

        self.retranslateUi(Dialog)
        self.queryBtn.clicked.connect(Dialog.queryWeather)
        self.clearBtn.clicked.connect(Dialog.clearText)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

windows_instance=window()