# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\fe14_sound_editor.ui',
# licensing of '.\fe14_sound_editor.ui' applies.
#
# Created: Mon Apr 27 09:20:54 2020
#      by: pyside2-uic  running on PySide2 5.13.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_sound_editor(object):
    def setupUi(self, indirect_sound_editor):
        indirect_sound_editor.setObjectName("sound_editor")
        indirect_sound_editor.resize(875, 516)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(indirect_sound_editor)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.widget = QtWidgets.QWidget(indirect_sound_editor)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.search_bar = QtWidgets.QLineEdit(self.widget)
        self.search_bar.setObjectName("search_bar")
        self.verticalLayout.addWidget(self.search_bar)
        self.sets_list_view = QtWidgets.QListView(self.widget)
        self.sets_list_view.setObjectName("sets_list_view")
        self.verticalLayout.addWidget(self.sets_list_view)
        self.horizontalLayout_3.addWidget(self.widget)
        self.line = QtWidgets.QFrame(indirect_sound_editor)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout_3.addWidget(self.line)
        self.widget_2 = QtWidgets.QWidget(indirect_sound_editor)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_2.sizePolicy().hasHeightForWidth())
        self.widget_2.setSizePolicy(sizePolicy)
        self.widget_2.setObjectName("widget_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.sounds_list_view = QtWidgets.QListView(self.widget_2)
        self.sounds_list_view.setObjectName("sounds_list_view")
        self.verticalLayout_2.addWidget(self.sounds_list_view)
        self.horizontalLayout_3.addWidget(self.widget_2)

        self.retranslateUi(indirect_sound_editor)
        QtCore.QMetaObject.connectSlotsByName(indirect_sound_editor)

    def retranslateUi(self, indirect_sound_editor):
        indirect_sound_editor.setWindowTitle(QtWidgets.QApplication.translate("indirect_sound_editor", "Form", None, -1))
        self.search_bar.setPlaceholderText(QtWidgets.QApplication.translate("indirect_sound_editor", "Search...", None, -1))

