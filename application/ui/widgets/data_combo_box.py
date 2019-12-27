from PySide2.QtWidgets import QComboBox

from services import service_locator
from .property_widget import PropertyWidget


class DataComboBox(QComboBox, PropertyWidget):
    def __init__(self, target_property_name, data_type, expected_type):
        QComboBox.__init__(self)
        PropertyWidget.__init__(self, target_property_name)
        data_service = service_locator.locator.get_scoped("ModuleDataService")
        self.data = data_service.entries[data_type]
        for (key, value) in self.data.items():
            if type(value) != expected_type:
                raise TypeError
            self.addItem(key, value)
        self.currentIndexChanged.connect(self._on_edit)

    def _on_edit(self, _index):
        value = self.currentData()
        self.commit(value)

    def _on_target_changed(self):
        if self.target:
            target_value = self._get_target_value()
            found = False
            i = 0
            while not found and i < len(self.data):
                if self.itemData(i) == target_value:
                    found = True
                else:
                    i += 1
            if i < len(self.data):
                self.setCurrentIndex(i)
            else:
                self.setCurrentIndex(0)
        else:
            self.setCurrentIndex(0)
