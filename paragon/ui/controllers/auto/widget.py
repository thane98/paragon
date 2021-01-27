from PySide2.QtWidgets import QWidget, QVBoxLayout

from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class Widget(AbstractAutoWidget, QWidget):
    def __init__(self, state, spec):
        AbstractAutoWidget.__init__(self, state)
        QWidget.__init__(self)
        if spec.margins:
            self.setContentsMargins(
                spec.margins[0], spec.margins[1], spec.margins[2], spec.margins[3]
            )
        self.inner = state.generator.generate(state, spec.id)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.inner)
        self.setLayout(layout)

    def set_target(self, rid):
        self.inner.set_target(rid)
