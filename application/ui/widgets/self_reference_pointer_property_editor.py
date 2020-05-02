from PySide2 import QtCore
from PySide2.QtWidgets import QComboBox
from .property_widget import PropertyWidget


class SelfReferencePointerPropertyEditor(QComboBox, PropertyWidget):
    def __init__(self, target_property_name, module):
        QComboBox.__init__(self)
        PropertyWidget.__init__(self, target_property_name)
        self.module = module
        self.setModel(module.entries_model)
        self.currentIndexChanged.connect(self._on_edit)
        self.setMaxVisibleItems(10)

    def _on_edit(self, index):
        model_index = self.model().index(index, 0)
        elem = self.model().data(model_index, QtCore.Qt.UserRole)
        if elem:
            self.commit(elem)

    def _on_target_changed(self):
        if self.target:
            found = False
            for i in range(0, len(self.module.entries)):
                elem = self.module.entries[i]
                target_value = self._get_target_value()
                if target_value == elem:
                    self.setCurrentIndex(i)
                    found = True
                    break
            if not found:
                self.setCurrentIndex(-1)
        else:
            self.setCurrentIndex(-1)
