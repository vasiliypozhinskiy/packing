# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'add_category.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Add_category(object):
    def setupUi(self, Add_category):
        Add_category.setObjectName("Add_category")
        Add_category.resize(389, 102)
        self.buttonBox = QtWidgets.QDialogButtonBox(Add_category)
        self.buttonBox.setGeometry(QtCore.QRect(30, 60, 351, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label = QtWidgets.QLabel(Add_category)
        self.label.setGeometry(QtCore.QRect(10, 10, 321, 20))
        self.label.setObjectName("label")
        self.lineEdit = QtWidgets.QLineEdit(Add_category)
        self.lineEdit.setGeometry(QtCore.QRect(10, 30, 371, 22))
        self.lineEdit.setObjectName("lineEdit")

        self.retranslateUi(Add_category)
        self.buttonBox.accepted.connect(Add_category.accept)
        self.buttonBox.rejected.connect(Add_category.reject)
        QtCore.QMetaObject.connectSlotsByName(Add_category)

    def retranslateUi(self, Add_category):
        _translate = QtCore.QCoreApplication.translate
        Add_category.setWindowTitle(_translate("Add_category", "Dialog"))
        self.label.setText(_translate("Add_category", "Enter category name"))
