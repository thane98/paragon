from PySide2.QtWidgets import QGroupBox, QVBoxLayout

from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class GroupBox(AbstractAutoWidget, QGroupBox):
    def __init__(self, state, spec):
        AbstractAutoWidget.__init__(self, state)
        QGroupBox.__init__(self)
        if spec.height:
            self.setFixedHeight(spec.height)
        if spec.title:
            self.setTitle(spec.title)
        if spec.flat:
            self.setFlat(True)
        self.inner = state.generator.generate_top_level(state, spec.inner)
        layout = QVBoxLayout()
        layout.addWidget(self.inner)
        self.setLayout(layout)

    def set_target(self, rid):
        self.inner.set_target(rid)
