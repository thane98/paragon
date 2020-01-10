from PySide2.QtWidgets import QWidget, QVBoxLayout, QLineEdit
from ui.widgets.property_widget import PropertyWidget


class MessagePropertyEditor (QWidget, PropertyWidget):
    def __init__(self, target_property_name):
        QWidget.__init__(self)
        PropertyWidget.__init__(self, target_property_name)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.key_editor = QLineEdit()
        self.value_editor = QLineEdit()
        layout.addWidget(self.key_editor)
        layout.addWidget(self.value_editor)
        self.setLayout(layout)

        self.key_editor.editingFinished.connect(self._on_key_edit)
        self.value_editor.editingFinished.connect(self._on_value_edit)

    def _on_key_edit(self):
        if self.target:
            target_prop = self.target[self.target_property_name]
            target_prop.update_key(self.key_editor.text())
            self.value_editor.setText(target_prop.value)

    def _on_value_edit(self):
        if self.target:
            target_prop = self.target[self.target_property_name]
            target_prop.value = self.value_editor.text()

    def _on_target_changed(self):
        if self.target:
            target_prop = self.target[self.target_property_name]
            self.key_editor.setText(target_prop.key)
            self.value_editor.setText(target_prop.value)
        else:
            self.key_editor.setText("")
            self.value_editor.setText("")
