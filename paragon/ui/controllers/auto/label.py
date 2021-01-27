from PySide2.QtWidgets import QLabel

from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class Label(AbstractAutoWidget, QLabel):
    def __init__(self, state, spec):
        AbstractAutoWidget.__init__(self, state)
        QLabel.__init__(self)
        self.setText(spec.text)
        self.setWordWrap(True)

    def set_target(self, rid):
        pass
