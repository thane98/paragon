from PySide6.QtWidgets import QScrollArea

from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class Scroll(AbstractAutoWidget, QScrollArea):
    def __init__(self, state, spec):
        AbstractAutoWidget.__init__(self, state)
        QScrollArea.__init__(self)
        self.inner = state.generator.generate_top_level(state, spec.inner)
        self.setWidget(self.inner)
        self.setWidgetResizable(True)

    def set_target(self, rid):
        self.inner.set_target(rid)
