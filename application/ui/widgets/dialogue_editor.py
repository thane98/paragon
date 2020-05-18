from typing import Optional

from PySide2.QtWidgets import QScrollArea, QWidget, QFormLayout, QLabel, QLineEdit

from module.properties.property_container import PropertyContainer
from services.service_locator import locator


class DialogueEditor(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = locator.get_scoped("DialogueService")
        self.service.load()
        self.target: Optional[PropertyContainer] = None
        form_container = QWidget()
        form = QFormLayout()
        self.editors = []
        for dialogue in self.service.dialogues:
            label = QLabel(dialogue.name)
            editor = QLineEdit()
            editor.editingFinished.connect(lambda e=editor, d=dialogue: self._on_editor_change(e, d))
            self.editors.append(editor)
            form.addRow(label, editor)
        form_container.setLayout(form)
        self.setWidget(form_container)
        self.setWidgetResizable(True)

    def _on_editor_change(self, editor, dialogue):
        if self.target:
            self.service.update_dialogue_value_for_character(self.target, dialogue, editor.text())

    def update_target(self, target: Optional[PropertyContainer]):
        self.target = target
        if target:
            for i in range(0, len(self.editors)):
                editor = self.editors[i]
                dialogue = self.service.dialogues[i]
                editor.setText(self.service.get_dialogue_value_for_character(self.target, dialogue))
        else:
            for editor in self.editors:
                editor.setText("")
        self.setEnabled(self.target is not None)
