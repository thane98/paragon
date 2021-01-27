from PySide2.QtWidgets import QWidget, QVBoxLayout
from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class VBox(AbstractAutoWidget, QWidget):
    def __init__(self, state, spec):
        AbstractAutoWidget.__init__(self, state)
        QWidget.__init__(self)
        layout = QVBoxLayout()
        layout.setSpacing(spec.spacing)
        layout.setContentsMargins(0, 0, 0, 0)
        self.widgets = []
        for inner_spec in spec.inner:
            w = state.generator.generate_top_level(state, inner_spec)
            layout.addWidget(w)
            self.widgets.append(w)
        self.setLayout(layout)

    def set_target(self, rid):
        for widget in self.widgets:
            widget.set_target(rid)
