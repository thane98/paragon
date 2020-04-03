from PySide2 import QtCore
from PySide2.QtCore import QModelIndex
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QListWidgetItem
from ui.autogen.ui_fe14_support_editor import Ui_support_editor
from services.service_locator import locator

SUPPORT_TYPE_TO_INDEX = {
    0x140E0904: 0,
    0xFF0E0904: 1,
    0x120C0703: 2,
    0xFF0C0703: 3
}

INDEX_TO_SUPPORT_TYPE = [0x140E0904, 0xFF0E0904, 0x120C0703, 0xFF0C0703]


class FE14SupportEditor(QWidget, Ui_support_editor):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        self.comboBox.setEnabled(False)
        self.setWindowTitle("Support Editor")
        self.setWindowIcon(QIcon("paragon.ico"))

        module_service = locator.get_scoped("ModuleService")
        self.service = None
        self.current_character = None
        self.current_supports = None
        self.current_support = None
        self.model = module_service.get_module("Characters").entries_model
        self.characters_list_view.setModel(self.model)

        self.characters_list_view.selectionModel().currentRowChanged.connect(self._update_selection)
        self.listWidget.selectionModel().currentRowChanged.connect(self._on_target_character_changed)
        self.listWidget_2.selectionModel().currentRowChanged.connect(self._update_support_selection)
        self.pushButton_2.clicked.connect(self._on_add_support_pressed)
        self.pushButton_3.clicked.connect(self._on_remove_support_pressed)
        self.comboBox.currentIndexChanged.connect(self._on_support_type_changed)

    def show(self):
        super().show()
        self.service = locator.get_scoped("SupportsService")

    def _update_selection(self, index: QtCore.QModelIndex):
        character = self.model.data(index, QtCore.Qt.UserRole)
        self._refresh_lists(character)
        self.current_character = character

    def _refresh_lists(self, character):
        self._update_supports_list(character)
        self._update_add_list(character)
        self.current_support = None
        self.comboBox.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)

    def _update_add_list(self, character):
        supported_characters = self._create_supported_characters_set(character)
        module_service = locator.get_scoped("ModuleService")

        self.listWidget.clear()
        characters = module_service.get_module("Characters").entries
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
        self.current_supports = supports

    def _get_model_index_of_character(self, character):
        module_service = locator.get_scoped("ModuleService")
        entries = module_service.get_module("Characters").entries
        for i in range(0, len(entries)):
            if entries[i] == character:
                return self.model.index(i)
        return QModelIndex()

    def _update_support_selection(self, index):
        if not index.isValid() or not self.current_supports:
            return
        self.current_support = self.current_supports[index.row()]
        index = SUPPORT_TYPE_TO_INDEX[self.current_support.support_type]
        self.comboBox.setCurrentIndex(index)
        self.comboBox.setEnabled(True)
        self.pushButton_3.setEnabled(True)

    def _on_support_type_changed(self, index):
        if not self.current_character or not self.current_support:
            return
        support_type = INDEX_TO_SUPPORT_TYPE[index]
        self.service.set_support_type(self.current_character, self.current_support, support_type)

    def _on_target_character_changed(self):
        self.pushButton_2.setEnabled(self.listWidget.currentIndex().isValid())

    def _on_add_support_pressed(self):
        if not self.current_character or not self.listWidget.currentIndex().isValid():
            return
        other_character = self.listWidget.currentItem().data(QtCore.Qt.UserRole)
        support_type = INDEX_TO_SUPPORT_TYPE[0]  # Default to romantic.
        self.service.add_support_between_characters(self.current_character, other_character, support_type)
        self._refresh_lists(self.current_character)

    def _on_remove_support_pressed(self):
        if not self.current_character or not self.current_support:
            return
        self.service.remove_support(self.current_character, self.current_support)
        self._refresh_lists(self.current_character)
