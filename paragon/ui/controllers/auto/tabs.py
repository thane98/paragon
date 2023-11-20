from PySide6.QtWidgets import QTabWidget
from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class Tabs(AbstractAutoWidget, QTabWidget):
    def __init__(self, state, spec):
        AbstractAutoWidget.__init__(self, state)
        QTabWidget.__init__(self)
        self.widgets = []
        for tab in spec.tabs:
            w = state.generator.generate_top_level(state, tab.inner)
            self.widgets.append(w)
            self.addTab(w, tab.title)

    def set_target(self, rid):
        for widget in self.widgets:
            widget.set_target(rid)

    def delete_tab(self, index):
        self.removeTab(index)
        del self.widgets[index]
