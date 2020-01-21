import logging

from PySide2 import QtWidgets, QtCore
from PySide2.QtWidgets import QWidget, QInputDialog
from properties.pointer_property import PointerProperty
from services.service_locator import locator
from ui.autogen.ui_simple_editor import Ui_simple_editor


class FE14ChapterCharactersTab(QWidget, Ui_simple_editor):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.module = None
        self.model = None
        self.selection = None

        self.proxy_model = QtCore.QSortFilterProxyModel()
        self.list_view.setModel(self.proxy_model)

        self.list_view.selectionModel().currentRowChanged.connect(self._update_selection)
        self.search_field.textChanged.connect(self._update_filter)
        self.add_button.clicked.connect(self._on_add_pressed)
        self.remove_button.clicked.connect(self._on_remove_pressed)
        self.copy_to_button.clicked.connect(self._on_copy_to_pressed)

        driver = locator.get_scoped("Driver")
        template = driver.common_modules["Person"].element_template
        self.editors = []
        for (key, prop) in template.items():
            label = QtWidgets.QLabel(key)
            editor = prop.create_editor()
            if editor:
                self.editors.append(editor)
                self.formLayout.addRow(label, editor)

        self.copy_to_button.setEnabled(False)
        self.remove_button.setEnabled(False)
        self.add_button.setEnabled(False)

    def update_chapter_data(self, chapter_data):
        if chapter_data.person:
            self.setEnabled(True)
            self.module = chapter_data.person
            self.model = self.module.entries_model
            self.proxy_model.setSourceModel(self.model)
        else:
            self.setEnabled(False)
        for editor in self.editors:
            editor.update_target(None)

    def _update_selection(self, index: QtCore.QModelIndex):
        self.selection = self.proxy_model.data(index, QtCore.Qt.UserRole)
        for editor in self.editors:
            editor.update_target(self.selection)
        self.remove_button.setEnabled(self.selection is not None)
        self.copy_to_button.setEnabled(self.selection is not None)

    def _update_filter(self):
        self.proxy_model.setFilterRegExp(self.search_field.text())

    def _on_add_pressed(self):
        # Add the new entry.
        self.model.insertRow(self.model.rowCount())

        # Copy the first entry's properties into the new entry.
        source = self.module.entries[0]
        dest = self.module.entries[len(self.module.entries) - 1]
        self._copy_properties(source, dest)

    def _on_remove_pressed(self):
        target_index = self.list_view.selectionModel().currentIndex()
        self.model.removeRow(target_index.row())

    def _on_copy_to_pressed(self):
        logging.info("Beginning copy to for " + self.module.name)

        choices = []
        for i in range(0, len(self.module.entries)):
            choices.append(str(i + 1) + ". " + self.model.data(self.model.index(i, 0), QtCore.Qt.DisplayRole))
        choice = QInputDialog.getItem(self, "Select Destination", "Destination", choices)

        if choice[1]:
            for i in range(0, len(choices)):
                if choice[0] == choices[i]:
                    self._copy_properties(self.selection, self.module.entries[i])
        else:
            logging.info("No choice selected for " + self.module.name + " copy to. Aborting.")

    @staticmethod
    def _copy_properties(source, destination):
        logging.info("Copying properties")

        for prop in source.values():
            prop.copy_to(destination)
            if type(prop) is PointerProperty:
                prop.copy_internal_pointer(source, destination)
