# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/bsdo/project/python/BSTrade/BSTrade/Component/View/Ui/ui_start_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_App(object):
    def setupUi(self, App):
        App.setObjectName("App")
        App.resize(499, 434)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(App)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.exchangeList = QtWidgets.QListWidget(App)
        self.exchangeList.setMaximumSize(QtCore.QSize(200, 16777215))
        self.exchangeList.setObjectName("exchangeList")
        self.horizontalLayout.addWidget(self.exchangeList)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.exchangeTitle = QtWidgets.QLabel(App)
        self.exchangeTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.exchangeTitle.setObjectName("exchangeTitle")
        self.verticalLayout.addWidget(self.exchangeTitle)
        self.openBtn = QtWidgets.QPushButton(App)
        self.openBtn.setCheckable(True)
        self.openBtn.setAutoDefault(False)
        self.openBtn.setDefault(False)
        self.openBtn.setFlat(False)
        self.openBtn.setObjectName("openBtn")
        self.verticalLayout.addWidget(self.openBtn)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(App)
        QtCore.QMetaObject.connectSlotsByName(App)

    def retranslateUi(self, App):
        _translate = QtCore.QCoreApplication.translate
        App.setWindowTitle(_translate("App", "StartDialog"))
        self.exchangeTitle.setText(_translate("App", "Bitmex"))
        self.openBtn.setText(_translate("App", "Open"))

