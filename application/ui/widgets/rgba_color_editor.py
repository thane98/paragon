import struct

from PySide2.QtGui import QColor
from PySide2.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy, QColorDialog, QPushButton

from ui.widgets.property_widget import PropertyWidget

_DEFAULT_COLOR = QColor(0, 0, 0)


class RGBAColorEditor(QWidget, PropertyWidget):
    def __init__(self, target_property_name):
        QWidget.__init__(self)
        PropertyWidget.__init__(self, target_property_name)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.color_label = QLabel()
        self.color_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.color_label.setFixedSize(50, 50)
        self.color_button = QPushButton("Change Color")
        self.color_button.pressed.connect(self._on_select_color_pressed)
        layout.addWidget(self.color_label)
        layout.addWidget(self.color_button)
        layout.addStretch()
        self._update_color_label(_DEFAULT_COLOR)
        self.setLayout(layout)

    def _update_color_label(self, color: QColor):
        color_string = hex(color.rgba())[2:].upper()
        style_string = "QLabel { border: 2px solid black; background-color: #%s }" % color_string
        self.color_label.setStyleSheet(style_string)

    def _on_select_color_pressed(self):
        if self.target:
            buffer = self.target[self.target_property_name].value
            old_color = QColor(buffer[0], buffer[1], buffer[2], buffer[3])
            new_color = QColorDialog.getColor(old_color, self, "Select Color", options=QColorDialog.ShowAlphaChannel)
            if not new_color.isValid():
                return

            new_color_bytes = struct.pack("<I", new_color.rgba())
            self.target[self.target_property_name].value = [
                new_color_bytes[2],
                new_color_bytes[1],
                new_color_bytes[0],
                new_color_bytes[3]
            ]
            self._update_color_label(new_color)

    def _on_target_changed(self):
        if self.target:
            buffer = self.target[self.target_property_name].value
            color = QColor(buffer[0], buffer[1], buffer[2], buffer[3])
            self._update_color_label(color)
        else:
            self._update_color_label(_DEFAULT_COLOR)
