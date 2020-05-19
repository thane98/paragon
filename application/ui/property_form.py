from typing import Optional

from PySide2 import QtWidgets
from PySide2.QtWidgets import QFormLayout, QScrollArea, QWidget

from module.properties.property_container import PropertyContainer


class PropertyForm(QFormLayout):
    def __init__(self, template: PropertyContainer, category=None, sort_editors=False):
        super().__init__()
        self.editors = {}
        editors_temp = []
        for (key, prop) in template.items():
            if category and prop.category != category:
                continue

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
            editors_temp.append((key, editor))
            self.editors[key] = editor

        if sort_editors:
            editors_temp.sort(key=lambda k: template[k[0]].sort_value)
        for key, editor in editors_temp:
            self.editors[key] = editor
            self.addRow(key, editor)

    @staticmethod
    def create_with_scroll(template: PropertyContainer) -> (QScrollArea, "PropertyForm"):
        form = PropertyForm(template)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_contents = QWidget()
        scroll_contents.setLayout(form)
        scroll.setWidget(scroll_contents)
        return scroll, form

    def update_target(self, target: Optional[PropertyContainer]):
        for editor in self.editors.values():
            editor.update_target(target)

    def fix_editor_width(self, width: int):
        for editor in self.editors.values():
            editor.setFixedWidth(width)
