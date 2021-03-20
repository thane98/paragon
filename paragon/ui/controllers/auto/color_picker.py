import struct

from PySide2.QtGui import QColor
from PySide2.QtWidgets import (
    QColorDialog,
)

from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget
from paragon.ui.views.ui_color_picker import Ui_ColorPicker

_DEFAULT_COLOR = QColor(0, 0, 0)


class ColorPicker(AbstractAutoWidget, Ui_ColorPicker):
    def __init__(self, state, field_id):
        AbstractAutoWidget.__init__(self, state)
        Ui_ColorPicker.__init__(self)
        self.field_id = field_id
        self.rid = None
        self.color_button.pressed.connect(self._on_select_color_pressed)
        self._update_color_label(_DEFAULT_COLOR)

    def _update_color_label(self, color: QColor):
        color_string = hex(color.rgba())[2:].upper()
        if color_string == "0":
            color_string = "00000000"
        style_string = (
            "QLabel {border: 2px solid black; background-color: #%s}" % color_string
        )
        self.color_label.setStyleSheet(style_string)

    def _on_select_color_pressed(self):
        if self.rid:
            buffer = self.data.bytes(self.rid, self.field_id)
            old_color = QColor(buffer[0], buffer[1], buffer[2], buffer[3])
            new_color = QColorDialog.getColor(
                old_color, self, "Select Color", options=QColorDialog.ShowAlphaChannel
            )
            if not new_color.isValid():
                return
            # TODO: Revisit this later. Not sure if this packing is correct.
            raw_color = struct.pack("<I", new_color.rgba())
            self.data.set_bytes(
                self.rid,
                self.field_id,
                bytearray(
                    [
                        raw_color[2],
                        raw_color[1],
                        raw_color[0],
                        raw_color[3],
                    ]
                ),
            )
            self._update_color_label(new_color)

    def set_target(self, rid):
        self.rid = rid
        if rid:
            buffer = self.data.bytes(rid, self.field_id)
            color = QColor(buffer[0], buffer[1], buffer[2], buffer[3])
            self._update_color_label(color)
        else:
            self._update_color_label(_DEFAULT_COLOR)
        self.setEnabled(self.rid is not None)
