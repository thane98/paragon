# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\table_editor.ui',
# licensing of '.\table_editor.ui' applies.
#
# Created: Fri May 15 21:12:31 2020
#      by: pyside2-uic  running on PySide2 5.13.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_TableEditor(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.splitter)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.search_bar = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.search_bar.setObjectName("search_bar")
        self.verticalLayout.addWidget(self.search_bar)
        self.list_view = QtWidgets.QListView(self.verticalLayoutWidget)
        self.list_view.setObjectName("list_view")
        self.verticalLayout.addWidget(self.list_view)
        self.scrollArea = QtWidgets.QScrollArea(self.splitter)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 243, 527))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.scroll_area_contents = QtWidgets.QWidget(self.scrollAreaWidgetContents)
        self.scroll_area_contents.setObjectName("scroll_area_contents")
        self.verticalLayout_3.addWidget(self.scroll_area_contents)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_2.addWidget(self.splitter)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.action_add = QtWidgets.QAction(MainWindow)
        self.action_add.setObjectName("action_add")
        self.action_delete = QtWidgets.QAction(MainWindow)
        self.action_delete.setObjectName("action_delete")
        self.action_export_csv = QtWidgets.QAction(MainWindow)
        self.action_export_csv.setObjectName("action_export_csv")
        self.action_import_csv = QtWidgets.QAction(MainWindow)
        self.action_import_csv.setObjectName("action_import_csv")
        self.action_copy_to = QtWidgets.QAction(MainWindow)
        self.action_copy_to.setObjectName("action_copy_to")
        self.toolBar.addAction(self.action_add)
        self.toolBar.addAction(self.action_delete)
        self.toolBar.addAction(self.action_copy_to)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.action_export_csv)
        self.toolBar.addAction(self.action_import_csv)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "MainWindow", None, -1))
        self.search_bar.setPlaceholderText(QtWidgets.QApplication.translate("MainWindow", "Search...", None, -1))
        self.toolBar.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "toolBar", None, -1))
        self.action_add.setText(QtWidgets.QApplication.translate("MainWindow", "Add", None, -1))
        self.action_delete.setText(QtWidgets.QApplication.translate("MainWindow", "Delete", None, -1))
        self.action_export_csv.setText(QtWidgets.QApplication.translate("MainWindow", "Export to CSV", None, -1))
        self.action_import_csv.setText(QtWidgets.QApplication.translate("MainWindow", "Import CSV", None, -1))
        self.action_copy_to.setText(QtWidgets.QApplication.translate("MainWindow", "Copy To", None, -1))

