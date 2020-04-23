from typing import Optional

from PySide2 import QtWidgets
from PySide2.QtWidgets import QFormLayout

from module.properties.property_container import PropertyContainer


class PropertyForm(QFormLayout):
    def __init__(self, template: PropertyContainer):
        super().__init__()
        self.editors = {}
        for (key, prop) in template.items():
            # Generate the editor label.
            label = QtWidgets.QLabel(key)
            if prop.tooltip:
                label.setToolTip(prop.tooltip)

            # Generate the actual editor.
            editor = prop.create_editor()
            if prop.is_disabled:
                editor.setEnabled(False)
            editor.form = self

            # Add a row to the form.
            self.editors[key] = editor
            self.addRow(label, editor)

    def update_target(self, target: Optional[PropertyContainer]):
        for editor in self.editors.values():
            editor.update_target(target)
