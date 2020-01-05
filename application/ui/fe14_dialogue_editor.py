from PySide2 import QtCore
from PySide2.QtWidgets import QSizePolicy
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QListView, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QScrollArea
from services.service_locator import locator


class FE14DialogueEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dialogue Editor")
        self.setWindowIcon(QIcon("paragon.ico"))

        driver = locator.get_scoped("Driver")
        self.model = driver.modules["Characters"].entries_model

        self.service = None
        self.editors = None
        self.loaded = False
        self.list = None

    def show(self):
        self._load()
        super().show()

    def _load(self):
        if self.loaded:
            return

        self.service = locator.get_scoped("DialogueService")
        driver = locator.get_scoped("Driver")

        layout = QHBoxLayout(self)
        characters_list = QListView()
        characters_list.setModel(driver.modules["Characters"].entries_model)
        characters_list.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding))
        characters_list.selectionModel().currentRowChanged.connect(self._update_selection)
        self.list = characters_list

        scroll_area = QScrollArea()
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
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(form_container)

        layout.addWidget(characters_list)
        layout.addWidget(scroll_area)
        self.setLayout(layout)

        self.service.load()
        self.loaded = True

    def _on_editor_change(self, editor, dialogue):
        character = self.model.data(self.list.currentIndex(), QtCore.Qt.UserRole)
        if character:
            self.service.update_dialogue_value_for_character(character, dialogue, editor.text())

    def _update_selection(self, index: QtCore.QModelIndex):
        # Sanity check
        if not self.loaded:
            return

        # Update fields
        character = self.model.data(index, QtCore.Qt.UserRole)
        for i in range(0, len(self.editors)):
            editor = self.editors[i]
            dialogue = self.service.dialogues[i]
            editor.setText(self.service.get_dialogue_value_for_character(character, dialogue))
