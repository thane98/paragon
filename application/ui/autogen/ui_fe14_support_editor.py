# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'fe14_support_editor.ui'
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

class Ui_support_editor(object):
    def setupUi(self, support_editor):
        if support_editor.objectName():
            support_editor.setObjectName(u"support_editor")
        support_editor.resize(875, 516)
        self.horizontalLayout_3 = QHBoxLayout(support_editor)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.lineEdit = QLineEdit(support_editor)
        self.lineEdit.setObjectName(u"lineEdit")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy)
        self.lineEdit.setMaximumSize(QSize(325, 16777215))

        self.verticalLayout.addWidget(self.lineEdit)

        self.characters_list_view = QListView(support_editor)
        self.characters_list_view.setObjectName(u"characters_list_view")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.characters_list_view.sizePolicy().hasHeightForWidth())
        self.characters_list_view.setSizePolicy(sizePolicy1)
        self.characters_list_view.setMinimumSize(QSize(325, 0))
        self.characters_list_view.setBaseSize(QSize(0, 0))

        self.verticalLayout.addWidget(self.characters_list_view)


        self.horizontalLayout_3.addLayout(self.verticalLayout)

        self.line = QFrame(support_editor)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout_3.addWidget(self.line)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.listWidget = QListWidget(support_editor)
        self.listWidget.setObjectName(u"listWidget")

        self.verticalLayout_2.addWidget(self.listWidget)

        self.widget = QWidget(support_editor)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout_2 = QHBoxLayout(self.widget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.pushButton_2 = QPushButton(self.widget)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setMaximumSize(QSize(70, 16777215))

        self.horizontalLayout_2.addWidget(self.pushButton_2)

        self.pushButton_3 = QPushButton(self.widget)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setMaximumSize(QSize(90, 16777215))

        self.horizontalLayout_2.addWidget(self.pushButton_3)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)


        self.verticalLayout_2.addWidget(self.widget)

        self.listWidget_2 = QListWidget(support_editor)
        self.listWidget_2.setObjectName(u"listWidget_2")

        self.verticalLayout_2.addWidget(self.listWidget_2)


        self.horizontalLayout_3.addLayout(self.verticalLayout_2)

        self.widget_2 = QWidget(support_editor)
        self.widget_2.setObjectName(u"widget_2")
        self.formLayout = QFormLayout(self.widget_2)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(self.widget_2)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.comboBox = QComboBox(self.widget_2)
        self.comboBox.addItem("Romantic")
        self.comboBox.addItem("Platonic")
        self.comboBox.addItem("Fast Romantic")
        self.comboBox.addItem("Fast Platonic")
        self.comboBox.setObjectName(u"comboBox")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.comboBox)


        self.horizontalLayout_3.addWidget(self.widget_2)


        self.retranslateUi(support_editor)

        QMetaObject.connectSlotsByName(support_editor)
    # setupUi

    def retranslateUi(self, support_editor):
        support_editor.setWindowTitle(QCoreApplication.translate("support_editor", u"Form", None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("support_editor", u"Search...", None))
        self.pushButton_2.setText(QCoreApplication.translate("support_editor", u"Add", None))
        self.pushButton_3.setText(QCoreApplication.translate("support_editor", u"Remove", None))
        self.label.setText(QCoreApplication.translate("support_editor", u"Type", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("support_editor", u"Romantic", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("support_editor", u"Platonic", None))
        self.comboBox.setItemText(2, QCoreApplication.translate("support_editor", u"Fast Romantic", None))
        self.comboBox.setItemText(3, QCoreApplication.translate("support_editor", u"Fast Platonic", None))

    # retranslateUi

