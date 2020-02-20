# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\error_dialog.ui',
# licensing of '.\error_dialog.ui' applies.
#
# Created: Thu Feb 20 17:41:18 2020
#      by: pyside2-uic  running on PySide2 5.13.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_error_dialog(object):
    def setupUi(self, error_dialog):
        error_dialog.setObjectName("error_dialog")
        error_dialog.resize(300, 100)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(error_dialog.sizePolicy().hasHeightForWidth())
        error_dialog.setSizePolicy(sizePolicy)
        self.verticalLayout = QtWidgets.QVBoxLayout(error_dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.error_label = QtWidgets.QLabel(error_dialog)
        self.error_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.error_label.setWordWrap(True)
        self.error_label.setObjectName("error_label")
        self.verticalLayout.addWidget(self.error_label)
        self.buttonBox = QtWidgets.QDialogButtonBox(error_dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(error_dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), error_dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), error_dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(error_dialog)

    def retranslateUi(self, error_dialog):
        error_dialog.setWindowTitle(QtWidgets.QApplication.translate("error_dialog", "An error has occurred.", None, -1))
        self.error_label.setText(QtWidgets.QApplication.translate("error_dialog", "TextLabel", None, -1))

