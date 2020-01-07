# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 5.14.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QFont,
    QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap,
    QRadialGradient)
from PySide2.QtWidgets import *

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(379, 422)
        self.action_save = QAction(MainWindow)
        self.action_save.setObjectName(u"action_save")
        self.action_close = QAction(MainWindow)
        self.action_close.setObjectName(u"action_close")
        self.action_quit = QAction(MainWindow)
        self.action_quit.setObjectName(u"action_quit")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout_2 = QVBoxLayout(self.tab)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.search_field = QLineEdit(self.tab)
        self.search_field.setObjectName(u"search_field")

        self.verticalLayout_2.addWidget(self.search_field)

        self.module_list_view = QListView(self.tab)
        self.module_list_view.setObjectName(u"module_list_view")

        self.verticalLayout_2.addWidget(self.module_list_view)

        self.tabWidget.addTab(self.tab, "Modules")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.verticalLayout_4 = QVBoxLayout(self.tab_3)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.editors_list_view = QListView(self.tab_3)
        self.editors_list_view.setObjectName(u"editors_list_view")

        self.verticalLayout_4.addWidget(self.editors_list_view)

        self.tabWidget.addTab(self.tab_3, "Dedicated Editors")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayout_3 = QVBoxLayout(self.tab_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.widget = QWidget(self.tab_2)
        self.widget.setObjectName(u"widget")
        self.widget.setLayoutDirection(Qt.RightToLeft)
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.close_button = QPushButton(self.widget)
        self.close_button.setObjectName(u"close_button")
        self.close_button.setEnabled(False)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.close_button.sizePolicy().hasHeightForWidth())
        self.close_button.setSizePolicy(sizePolicy)
        self.close_button.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout.addWidget(self.close_button)


        self.verticalLayout_3.addWidget(self.widget)

        self.file_list_view = QListView(self.tab_2)
        self.file_list_view.setObjectName(u"file_list_view")

        self.verticalLayout_3.addWidget(self.file_list_view)

        self.tabWidget.addTab(self.tab_2, "Open Files")

        self.verticalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 379, 42))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menuFile.addAction(self.action_save)
        self.menuFile.addAction(self.action_close)
        self.menuFile.addAction(self.action_quit)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.action_save.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.action_close.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.action_quit.setText(QCoreApplication.translate("MainWindow", u"Quit", None))
        self.search_field.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Search...", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Modules", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("MainWindow", u"Dedicated Editors", None))
        self.close_button.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"Open Files", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
    # retranslateUi

