from PySide2 import QtCore
from PySide2.QtWidgets import QComboBox

from .property_widget import PropertyWidget


class ReferencePropertyEditor(QComboBox, PropertyWidget):
    def __init__(self, target_property_name, module, other_property_name):
        QComboBox.__init__(self)
        PropertyWidget.__init__(self, target_property_name)
        self.module = module
        self.other_property_name = other_property_name
        self.setModel(module.entries_model)
        self.currentIndexChanged.connect(self._on_edit)
        self.setMaxVisibleItems(10)

    def _on_edit(self, index):
        model_index = self.model().index(index, 0)
        elem = self.model().data(model_index, QtCore.Qt.UserRole)
        if elem:
            self.commit(elem[self.other_property_name].value)

    def _on_target_changed(self):
        if self.target:
            found = False
            for i in range(0, len(self.module.entries)):
                elem = self.module.entries[i]
                other_value = elem[self.other_property_name].value
                target_value = self._get_target_value()
                if target_value == other_value:
                    self.setCurrentIndex(i)
                    found = True
                    break
            if not found:
                self.setCurrentIndex(0)
        else:
            self.setCurrentIndex(0)
