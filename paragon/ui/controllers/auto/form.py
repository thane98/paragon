from PySide2.QtWidgets import QWidget, QFormLayout, QLabel
from paragon.ui import utils
from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


def _get_label_text(field_id, name):
    if name:
        return name
    else:
        return " ".join(map(lambda s: s.capitalize(), field_id.split("_")))


class Form(AbstractAutoWidget, QWidget):
    def __init__(self, state, spec):
        AbstractAutoWidget.__init__(self, state)
        QWidget.__init__(self)

        self.widgets = []
        layout = QFormLayout()
        ids = spec.ids if spec.ids else state.field_metadata
        for field_id in ids:
            fm = state.field_metadata[field_id]
            label = QLabel(utils.capitalize(field_id, fm["name"]))
            widget = state.generator.generate(state, field_id)
            layout.addRow(label, widget)
            self.widgets.append(widget)
        self.setLayout(layout)

    def set_target(self, rid):
        for widget in self.widgets:
            widget.set_target(rid)
