from typing import Optional

from PySide2 import QtWidgets
from PySide2.QtWidgets import QFormLayout

from module.properties.property_container import PropertyContainer


class PropertyForm(QFormLayout):
    def __init__(self, template: PropertyContainer):
        super().__init__()
        self.editors = {}
        for (key, prop) in template.items():
            label = QtWidgets.QLabel(key)
            editor = prop.create_editor()
            if prop.is_disabled:
                editor.setEnabled(False)
            editor.form = self
            self.editors[key] = editor
            self.addRow(label, editor)

    def update_target(self, target: Optional[PropertyContainer]):
        for editor in self.editors.values():
            editor.update_target(target)
