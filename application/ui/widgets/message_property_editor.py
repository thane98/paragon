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

        self.key_editor.editingFinished.connect(self._on_edit)
        self.value_editor.editingFinished.connect(self._on_edit)

    def _on_edit(self):
        if self.target:
            target_prop = self.target[self.target_property_name]
            target_prop.key = self.key_editor.text()
            target_prop.value = self.value_editor.text().replace("\\n", '\n')

    def _on_target_changed(self):
        if self.target:
            target_prop = self.target[self.target_property_name]
            self.key_editor.setText(target_prop.key)
            self.value_editor.setText(target_prop.value.replace('\n', "\\n"))
        else:
            self.key_editor.setText("")
            self.value_editor.setText("")
