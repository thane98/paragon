# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\project_select.ui',
# licensing of '.\project_select.ui' applies.
#
# Created: Mon May  4 10:57:45 2020
#      by: pyside2-uic  running on PySide2 5.13.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_project_select(object):
    def setupUi(self, project_select):
        project_select.setObjectName("project_select")
        project_select.resize(591, 358)
        self.centralwidget = QtWidgets.QWidget(project_select)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.table_view = QtWidgets.QTableView(self.centralwidget)
        self.table_view.setObjectName("table_view")
        self.verticalLayout.addWidget(self.table_view)
        self.remember_check_box = QtWidgets.QCheckBox(self.centralwidget)
        self.remember_check_box.setObjectName("remember_check_box")
        self.verticalLayout.addWidget(self.remember_check_box)
        project_select.setCentralWidget(self.centralwidget)
        self.toolBar = QtWidgets.QToolBar(project_select)
        self.toolBar.setObjectName("toolBar")
        project_select.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolBar)
        self.action_create = QtWidgets.QAction(project_select)
        self.action_create.setObjectName("action_create")
        self.action_remove = QtWidgets.QAction(project_select)
        self.action_remove.setObjectName("action_remove")
        self.action_move_up = QtWidgets.QAction(project_select)
        self.action_move_up.setObjectName("action_move_up")
        self.action_move_down = QtWidgets.QAction(project_select)
        self.action_move_down.setObjectName("action_move_down")
        self.toolBar.addAction(self.action_create)
        self.toolBar.addAction(self.action_remove)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.action_move_up)
        self.toolBar.addAction(self.action_move_down)

        self.retranslateUi(project_select)
        QtCore.QMetaObject.connectSlotsByName(project_select)

    def retranslateUi(self, project_select):
        project_select.setWindowTitle(QtWidgets.QApplication.translate("project_select", "MainWindow", None, -1))
        self.remember_check_box.setText(QtWidgets.QApplication.translate("project_select", "Remember my selection.", None, -1))
        self.toolBar.setWindowTitle(QtWidgets.QApplication.translate("project_select", "toolBar", None, -1))
        self.action_create.setText(QtWidgets.QApplication.translate("project_select", "Create", None, -1))
        self.action_remove.setText(QtWidgets.QApplication.translate("project_select", "Remove", None, -1))
        self.action_move_up.setText(QtWidgets.QApplication.translate("project_select", "Move Up", None, -1))
        self.action_move_down.setText(QtWidgets.QApplication.translate("project_select", "Move Down", None, -1))

