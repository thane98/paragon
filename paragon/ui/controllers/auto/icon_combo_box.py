from PySide2.QtWidgets import QComboBox

from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class IconComboBox(AbstractAutoWidget, QComboBox):
    def __init__(self, state, spec, field_id):
        AbstractAutoWidget.__init__(self, state)
        QComboBox.__init__(self)
        self.setModel(self.gs.icons.model(spec.icons))
        self.setStyleSheet("combobox-popup: 0;")
        self.field_id = field_id
        self.rid = None
        self.base_index = spec.base_index

        self.currentIndexChanged.connect(self._on_edit)

    def set_target(self, rid):
        self.rid = rid
        if rid:
            value = self.base_index + self.data.int(self.rid, self.field_id)
            if value in range(0, self.model().rowCount()):
                self.setCurrentIndex(value)
            else:
                self.setCurrentIndex(-1)
        else:
            self.setCurrentIndex(-1)
        self.setEnabled(self.rid is not None)

    def _on_edit(self):
        if self.rid:
            value = self.currentIndex() - self.base_index
            self.data.set_int(self.rid, self.field_id, value)
