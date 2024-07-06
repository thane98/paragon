from PySide6.QtWidgets import QWidget, QComboBox, QVBoxLayout

from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class Swappable(AbstractAutoWidget, QWidget):
    def __init__(self, state, spec, field_id):
        AbstractAutoWidget.__init__(self, state)
        QWidget.__init__(self)

        self.spec = spec
        self.rid = None
        self.field_id = field_id

        self.setContentsMargins(0, 0, 0, 0)
        self.options = QComboBox()
        self.options.addItems(spec.names)
        self.widgets = []
        layout = QVBoxLayout()
        layout.addWidget(self.options)
        layout.setContentsMargins(0, 0, 0, 0)
        for widget_spec in spec.widgets:
            widget = state.generator.generate(state, field_id, spec=widget_spec)
            layout.addWidget(widget)
            self.widgets.append(widget)
        self.setLayout(layout)

        self._set_option(0)

        self.options.currentIndexChanged.connect(self._set_option)

    def set_target(self, rid):
        self.rid = rid
        self.widgets[self.options.currentIndex()].set_target(rid)

    def _set_option(self, index):
        if self.options.currentIndex() != index:
            self.options.setCurrentIndex(index)
        for i in range(0, len(self.widgets)):
            if i == index:
                self.widgets[i].setVisible(True)
                self.widgets[i].set_target(self.rid)
            else:
                self.widgets[i].setVisible(False)
