from PySide2.QtWidgets import QWidget, QHBoxLayout
from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class HBox(AbstractAutoWidget, QWidget):
    def __init__(self, state, spec):
        AbstractAutoWidget.__init__(self, state)
        QWidget.__init__(self)
        layout = QHBoxLayout()
        layout.setSpacing(spec.spacing)
        layout.setContentsMargins(0, 0, 0, 0)
        if spec.height:
            self.setFixedHeight(spec.height)
        self.widgets = []
        for inner_spec in spec.inner:
            w = state.generator.generate_top_level(state, inner_spec)
            layout.addWidget(w)
            self.widgets.append(w)
        if spec.stretch_index:
            layout.setStretch(spec.stretch_index, 1)
        self.setLayout(layout)

    def set_target(self, rid):
        for widget in self.widgets:
            widget.set_target(rid)
