import logging

from PySide6.QtWidgets import QComboBox
from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class DataComboBox(AbstractAutoWidget, QComboBox):
    def __init__(self, state, spec, field_id):
        AbstractAutoWidget.__init__(self, state)
        QComboBox.__init__(self)
        self.setStyleSheet("combobox-popup: 0;")
        self.type = spec.target_type
        self.rid = None
        self.field_id = field_id
        if spec.enum:
            self.enum_data = self.gs.enums.load(spec.enum)
        else:
            self.enum_data = spec.items
        for key in self.enum_data:
            self.addItem(key, self.enum_data[key])
        self.currentIndexChanged.connect(self._on_edit)

    def _on_edit(self):
        if self.rid and self.currentData() is not None:
            if self.type == "string":
                self.data.set_string(self.rid, self.field_id, self.currentData())
            elif self.type == "float":
                self.data.set_float(self.rid, self.field_id, self.currentData())
            else:
                self.data.set_int(self.rid, self.field_id, self.currentData())

    def _get_value(self):
        if self.type == "string":
            return self.data.string(self.rid, self.field_id)
        elif self.type == "float":
            return self.data.float(self.rid, self.field_id)
        else:
            return self.data.int(self.rid, self.field_id)

    def set_target(self, rid):
        self.rid = rid
        if self.rid:
            target_value = self._get_value()
            found = False
            i = 0
            while not found and i < len(self.enum_data):
                if self.itemData(i) == target_value:
                    found = True
                else:
                    i += 1
            if not found:
                logging.warning(
                    f"unrecognized value '{target_value}' for field '{self.field_id}'. Using default..."
                )
            self.setCurrentIndex(i if found else -1)
        else:

            self.setCurrentIndex(-1)
        self.setEnabled(self.rid is not None)
