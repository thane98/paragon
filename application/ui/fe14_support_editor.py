from PySide2 import QtCore
from PySide2.QtCore import QModelIndex
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QListWidgetItem

from ui.autogen.ui_fe14_support_editor import Ui_support_editor
from services.service_locator import locator


class FE14SupportEditor(QWidget, Ui_support_editor):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        self.setWindowTitle("Support Editor")
        self.setWindowIcon(QIcon("paragon.ico"))

        driver = locator.get_scoped("Driver")
        self.service = None
        self.model = driver.modules["Characters"].entries_model
        self.characters_list_view.setModel(self.model)
        self.characters_list_view.selectionModel().currentRowChanged.connect(self._update_selection)

    def show(self):
        super().show()
        self.service = locator.get_scoped("SupportsService")

    def _update_selection(self, index: QtCore.QModelIndex):
        character = self.model.data(index, QtCore.Qt.UserRole)
        self._update_supports_list(character)
        self._update_add_list(character)

    def _update_add_list(self, character):
        supported_characters = self._create_supported_characters_set(character)
        driver = locator.get_scoped("Driver")

        self.listWidget.clear()
        characters = driver.modules["Characters"].entries
        for target_character in characters:
            if target_character["PID"] not in supported_characters:
                model_index = self._get_model_index_of_character(target_character)
                display_name = self.model.data(model_index, QtCore.Qt.DisplayRole)
                item = QListWidgetItem(display_name)
                item.setData(QtCore.Qt.UserRole, target_character)
                self.listWidget.addItem(item)

    # Dict is not hashable. PIDs should be unique, so we'll use those instead.
    # Might be able to use IDs instead.
    def _create_supported_characters_set(self, character):
        supports = self.service.get_supports_for_character(character)
        result = set()
        for support in supports:
            result.add(support.character["PID"])
        return result

    def _update_supports_list(self, character):
        supports = self.service.get_supports_for_character(character)
        self.listWidget_2.clear()
        for support in supports:
            model_index = self._get_model_index_of_character(support.character)
            display_name = self.model.data(model_index, QtCore.Qt.DisplayRole)
            item = QListWidgetItem(display_name)
            item.setData(QtCore.Qt.UserRole, support)
            self.listWidget_2.addItem(item)

    def _get_model_index_of_character(self, character):
        driver = locator.get_scoped("Driver")
        entries = driver.modules["Characters"].entries
        for i in range(0, len(entries)):
            if entries[i] == character:
                return self.model.index(i)
        return QModelIndex()
