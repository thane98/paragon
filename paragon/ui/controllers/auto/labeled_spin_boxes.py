from PySide2.QtWidgets import QFormLayout, QWidget, QSpinBox
from paragon.ui.controllers.auto.abstract_spin_boxes import AbstractSpinBoxes


class LabeledSpinBoxes(AbstractSpinBoxes, QWidget):
    def __init__(self, state, spec, field_id):
        AbstractSpinBoxes.__init__(self, state, field_id)
        QWidget.__init__(self)
        layout = QFormLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        for i in range(0, min(self.length, len(spec.labels))):
            editor = QSpinBox()
            editor.setRange(-128, 127)
            editor.valueChanged.connect(self.save)
            self.editors.append(editor)
            layout.addRow(spec.labels[i], editor)
        self.setLayout(layout)

    def _post_set_target(self):
        self.setEnabled(self.rid is not None)
