import struct

from PySide2.QtWidgets import QWidget, QGridLayout, QSpinBox, QLabel
from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget
from paragon.ui import utils


class SpinBoxMatrix(AbstractAutoWidget, QWidget):
    def __init__(self, state, spec):
        AbstractAutoWidget.__init__(self, state)
        QWidget.__init__(self)

        self.rid = None
        self.spec = spec
        self.spin_boxes = []

        fm = state.field_metadata
        layout = QGridLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        for i in range(0, len(self.spec.columns)):
            label = QLabel(self.spec.columns[i])
            layout.addWidget(label, 0, i + 1)
        for r in range(0, len(self.spec.ids)):
            field_id = self.spec.ids[r]
            name = fm[field_id]["name"]
            label = QLabel(utils.capitalize(field_id, name))
            layout.addWidget(label, r + 1, 0)
            row_widgets = []
            num_columns = spec.column_counts[r] if spec.column_counts else len(spec.columns)
            for c in range(0, num_columns):
                spin_box = QSpinBox()
                spin_box.setRange(-128, 127)
                spin_box.valueChanged.connect(
                    lambda v, row=r, col=c: self._update_value(row, col, v)
                )
                layout.addWidget(spin_box, r + 1, c + 1)
                row_widgets.append(spin_box)
            self.spin_boxes.append(row_widgets)
        for i in range(0, len(self.spec.columns)):
            layout.setColumnStretch(i + 1, 1)
        self.setLayout(layout)
        self.setFixedHeight(self.spec.height)

    def set_target(self, rid):
        self.rid = rid
        for r in range(0, len(self.spec.ids)):
            num_columns = self.spec.column_counts[r] if self.spec.column_counts else len(self.spec.columns)
            if rid:
                field_id = self.spec.ids[r]
                row_values = self.data.bytes(rid, field_id)
            else:
                row_values = [0] * num_columns
            for c in range(0, num_columns):
                value = 0 if not rid else row_values[c]
                unsigned_value = struct.pack("B", value)
                signed_value = int(struct.unpack("b", unsigned_value)[0])
                self.spin_boxes[r][c].setValue(signed_value)
                self.spin_boxes[r][c].setEnabled(rid is not None)

    def _update_value(self, row, column, value):
        if self.rid:
            field_id = self.spec.ids[row]
            signed_value = struct.pack("b", value)
            buffer = self.data.bytes(self.rid, field_id)
            buffer[column] = int(struct.unpack("B", signed_value)[0])
            self.data.set_bytes(self.rid, field_id, buffer)
