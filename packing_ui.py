# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'packing.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(722, 630)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.App_info = QtWidgets.QTextBrowser(self.centralwidget)
        self.App_info.setGeometry(QtCore.QRect(10, 10, 701, 31))
        self.App_info.setObjectName("App_info")
        self.treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        self.treeWidget.setGeometry(QtCore.QRect(10, 90, 550, 430))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeWidget.sizePolicy().hasHeightForWidth())
        self.treeWidget.setSizePolicy(sizePolicy)
        self.treeWidget.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.treeWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.treeWidget.setDragDropMode(QtWidgets.QAbstractItemView.NoDragDrop)
        self.treeWidget.setColumnCount(0)
        self.treeWidget.setObjectName("treeWidget")
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(12, 50, 501, 22))
        self.comboBox.setObjectName("comboBox")
        self.toolButton = QtWidgets.QToolButton(self.centralwidget)
        self.toolButton.setGeometry(QtCore.QRect(520, 50, 31, 21))
        self.toolButton.setObjectName("toolButton")
        self.Delete_button = QtWidgets.QPushButton(self.centralwidget)
        self.Delete_button.setGeometry(QtCore.QRect(570, 90, 141, 28))
        self.Delete_button.setObjectName("Delete_button")
        self.Add_category_button = QtWidgets.QPushButton(self.centralwidget)
        self.Add_category_button.setGeometry(QtCore.QRect(570, 130, 141, 28))
        self.Add_category_button.setObjectName("Add_category_button")
        self.Add_item_button = QtWidgets.QPushButton(self.centralwidget)
        self.Add_item_button.setGeometry(QtCore.QRect(570, 170, 141, 28))
        self.Add_item_button.setObjectName("Add_item_button")
        self.lcdNumber = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdNumber.setGeometry(QtCore.QRect(460, 520, 101, 51))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.lcdNumber.setFont(font)
        self.lcdNumber.setLineWidth(2)
        self.lcdNumber.setMode(QtWidgets.QLCDNumber.Dec)
        self.lcdNumber.setObjectName("lcdNumber")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(380, 530, 71, 31))
        self.label.setObjectName("label")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 722, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.treeWidget.setSortingEnabled(True)
        self.toolButton.setText(_translate("MainWindow", "..."))
        self.Delete_button.setText(_translate("MainWindow", "Удалить элемент"))
        self.Add_category_button.setText(_translate("MainWindow", "Добавить категорию"))
        self.Add_item_button.setText(_translate("MainWindow", "Добавить предмет"))
        self.label.setText(_translate("MainWindow", "Общий вес:"))
