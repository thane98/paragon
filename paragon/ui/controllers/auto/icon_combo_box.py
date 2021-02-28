from PySide2.QtWidgets import QComboBox

from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget
from PySide2.QtCore import QSize

class IconComboBox(AbstractAutoWidget, QComboBox):
    def __init__(self, state, spec, field_id):
        AbstractAutoWidget.__init__(self, state)
        QComboBox.__init__(self)
        self.setModel(self.gs.icons.model(spec.icons))
        self.setStyleSheet("combobox-popup: 0;")
        self.field_id = field_id
        if spec.icons == "skill":
            self.setIconSize(QSize(24, 24))
        elif spec.icons == "item":
            self.setIconSize(QSize(16, 16))
        self.rid = None
        self.currentIndexChanged.connect(self._on_edit)

    def set_target(self, rid):
        self.rid = rid
        if rid:
            value = self.data.int(self.rid, self.field_id)
            if value in range(0, self.model().rowCount()):
                self.setCurrentIndex(value)
            else:
                self.setCurrentIndex(0)
        else:
            self.setCurrentIndex(-1)
        self.setEnabled(self.rid is not None)

    def _on_edit(self):
        if self.rid and self.currentIndex() >= 0:
            self.data.set_int(self.rid, self.field_id, self.currentIndex())
