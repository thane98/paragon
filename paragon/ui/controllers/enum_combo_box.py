from typing import Optional

from PySide2 import QtCore
from PySide2.QtWidgets import QComboBox


class EnumComboBox(QComboBox):
    def __init__(self, enum, parent=None):
        super().__init__(parent)
        self.enum = enum

        for _, value in self.enum.__members__.items():
            self.addItem(value, value)
        self.setCurrentIndex(-1)

    def value(self) -> Optional:
        return self.currentData(QtCore.Qt.UserRole)
