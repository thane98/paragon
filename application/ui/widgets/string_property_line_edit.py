from PySide2.QtWidgets import QLineEdit
from .property_widget import PropertyWidget


class StringPropertyLineEdit(QLineEdit, PropertyWidget):
    def __init__(self, target_property_name):
        QLineEdit.__init__(self)
        PropertyWidget.__init__(self, target_property_name)
        self.editingFinished.connect(self._on_edit)

    def _on_edit(self):
        if self.target:
            target_property = self.target[self.target_property_name]
            target_property.set_value(self.text())
            if target_property.linked_property:
                editor = self.form.editors[target_property.linked_property]
                editor.setText(self.text())

    def _on_target_changed(self):
        if self.target:
            self.setText(self._get_target_value())
        else:
            self.setText("")
