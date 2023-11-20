from PySide6.QtWidgets import QWidget, QHBoxLayout, QSpinBox
from paragon.ui.controllers.auto.abstract_spin_boxes import AbstractSpinBoxes


class SpinBoxes(AbstractSpinBoxes, QWidget):
    def __init__(self, state, field_id):
        AbstractSpinBoxes.__init__(self, state, field_id)
        QWidget.__init__(self)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        for i in range(0, self.length):
            editor = QSpinBox()
            editor.setRange(-128, 127)
            editor.valueChanged.connect(self.save)
            self.editors.append(editor)
            layout.addWidget(editor)
        self.setLayout(layout)

    def disconnect_boxes(self):
        for editor in self.editors:
            editor.disconnect(self)

    def _post_set_target(self):
        self.setEnabled(self.rid is not None)
