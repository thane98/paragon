# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\main_window.ui',
# licensing of '.\main_window.ui' applies.
#
# Created: Mon Dec 23 13:52:16 2019
#      by: pyside2-uic  running on PySide2 5.13.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(379, 422)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.search_field = QtWidgets.QLineEdit(self.centralwidget)
        self.search_field.setObjectName("search_field")
        self.verticalLayout.addWidget(self.search_field)
        self.module_list_view = QtWidgets.QListView(self.centralwidget)
        self.module_list_view.setObjectName("module_list_view")
        self.verticalLayout.addWidget(self.module_list_view)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 379, 26))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action_save = QtWidgets.QAction(MainWindow)
        self.action_save.setObjectName("action_save")
        self.action_close = QtWidgets.QAction(MainWindow)
        self.action_close.setObjectName("action_close")
        self.action_quit = QtWidgets.QAction(MainWindow)
        self.action_quit.setObjectName("action_quit")
        self.menuFile.addAction(self.action_save)
        self.menuFile.addAction(self.action_close)
        self.menuFile.addAction(self.action_quit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "MainWindow", None, -1))
        self.search_field.setPlaceholderText(QtWidgets.QApplication.translate("MainWindow", "Search...", None, -1))
        self.menuFile.setTitle(QtWidgets.QApplication.translate("MainWindow", "File", None, -1))
        self.action_save.setText(QtWidgets.QApplication.translate("MainWindow", "Save", None, -1))
        self.action_close.setText(QtWidgets.QApplication.translate("MainWindow", "Close", None, -1))
        self.action_quit.setText(QtWidgets.QApplication.translate("MainWindow", "Quit", None, -1))

