import ctypes

from PySide2 import QtGui
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QSpinBox, QWidget, QHBoxLayout

from .property_widget import PropertyWidget


class CoordinateWidget(QWidget, PropertyWidget):
    position_changed = Signal(int, int)

    def __init__(self, target_property_name):
        QWidget.__init__(self)
        PropertyWidget.__init__(self, target_property_name)
        self.layout = QHBoxLayout()
        self.x_spinbox = QSpinBox()
        self.y_spinbox = QSpinBox()
        self.x_spinbox.setRange(-128, 127)
        self.y_spinbox.setRange(-128, 127)
        self.x_spinbox.setFixedWidth(60)
        self.y_spinbox.setFixedWidth(60)
        self.layout.addWidget(self.x_spinbox)
        self.layout.addWidget(self.y_spinbox)
        self.layout.setAlignment(QtGui.Qt.AlignLeft)
        self.setLayout(self.layout)
        self.x_spinbox.valueChanged.connect(lambda v: self._on_edit(v, 0))
        self.y_spinbox.valueChanged.connect(lambda v: self._on_edit(v, 1))
        self.is_disable_write_back = False

    def _on_edit(self, value, index):
        if self.target:
            buffer = self.target[self.target_property_name].value
            if buffer[index] != value:
                if not self.is_disable_write_back:
                    buffer[index] = self._signed_to_unsigned(value)
                self.position_changed.emit(self.x_spinbox.value(), self.y_spinbox.value())

    def _on_target_changed(self):
        if self.target:
            buffer = self.target[self.target_property_name].value
            self.x_spinbox.setValue(self._unsigned_to_signed(buffer[0]))
            self.y_spinbox.setValue(self._unsigned_to_signed(buffer[1]))
        else:
            self.x_spinbox.setValue(0)
            self.y_spinbox.setValue(0)

    @staticmethod
    def _unsigned_to_signed(value):
        packed = ctypes.c_byte(value)
        return packed.value

    @staticmethod
    def _signed_to_unsigned(value):
        packed = ctypes.c_ubyte(value)
        return packed.value

    def set_disable_write_back(self, is_disabled: bool):
        self.is_disable_write_back = is_disabled
