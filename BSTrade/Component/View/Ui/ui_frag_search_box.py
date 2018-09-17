# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/bsdo/project/python/BSTrade/BSTrade/Component/View/Ui/ui_frag_search_box.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_GroupBox(object):
    def setupUi(self, GroupBox):
        GroupBox.setObjectName("GroupBox")
        GroupBox.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(GroupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.searchBar = QtWidgets.QLineEdit(GroupBox)
        self.searchBar.setObjectName("searchBar")
        self.verticalLayout.addWidget(self.searchBar)
        self.searchList = QtWidgets.QListView(GroupBox)
        self.searchList.setObjectName("searchList")
        self.verticalLayout.addWidget(self.searchList)

        self.retranslateUi(GroupBox)
        QtCore.QMetaObject.connectSlotsByName(GroupBox)

    def retranslateUi(self, GroupBox):
        _translate = QtCore.QCoreApplication.translate
        GroupBox.setWindowTitle(_translate("GroupBox", "GroupBox"))
        GroupBox.setTitle(_translate("GroupBox", "Groupbox"))

