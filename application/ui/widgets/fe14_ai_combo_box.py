from PySide2.QtWidgets import QComboBox

from services import service_locator
from .property_widget import PropertyWidget


class FE14AIComboBox(QComboBox, PropertyWidget):
    def __init__(self, target_property_name, label_name):
        QComboBox.__init__(self)
        PropertyWidget.__init__(self, target_property_name)
        self.data = self._get_data_from_label_name(label_name)
        for label in self.data:
            self.addItem(label, label)
        self.currentIndexChanged.connect(self._on_edit)

    @staticmethod
    def _get_data_from_label_name(label_name: str):
        ai_data_service = service_locator.locator.get_scoped("AIDataService")
        if label_name == "ac":
            return ai_data_service.get_ac_labels()
        elif label_name == "at":
            return ai_data_service.get_at_labels()
        elif label_name == "mi":
            return ai_data_service.get_mi_labels()
        else:
            return ai_data_service.get_mv_labels()

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
