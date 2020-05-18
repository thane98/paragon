from typing import Optional, List

from PySide2 import QtCore
from PySide2.QtWidgets import QListWidgetItem, QListWidget

from module.properties.property_container import PropertyContainer
from services.fe14.supports_service import Support
from services.service_locator import locator
from ui.views.ui_fe14_support_widget import Ui_FE14SupportWidget

SUPPORT_TYPE_TO_INDEX = {
    0x140E0904: 0,
    0xFF0E0904: 1,
    0x120C0703: 2,
    0xFF0C0703: 3
}

INDEX_TO_SUPPORT_TYPE = [0x140E0904, 0xFF0E0904, 0x120C0703, 0xFF0C0703]


class FE14SupportWidget(Ui_FE14SupportWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.characters_module = locator.get_scoped("ModuleService").get_module("Characters")
        self.service = locator.get_scoped("SupportsService")
        self.target: Optional[PropertyContainer] = None
        self.current_character: Optional[PropertyContainer] = None
        self.current_supports: Optional[List[Support]] = None
        self.current_support: Optional[Support] = None

        self.characters_widget.selectionModel().currentRowChanged.connect(self._update_current_character)
        self.supports_widget.selectionModel().currentRowChanged.connect(self._update_current_support)
        self.add_button.clicked.connect(self._on_add_support_pressed)
        self.remove_button.clicked.connect(self._on_remove_support_pressed)
        self.support_type_box.currentIndexChanged.connect(self._on_support_type_changed)

    def update_target(self, target: Optional[PropertyContainer]):
        self.target = target
        self._clear()
        if target:
            self._refresh_add_list()
            self._refresh_supports_list()
        self.setEnabled(self.target is not None)

    def _clear(self):
        self.characters_widget.clear()
        self.supports_widget.clear()
        self.support_type_box.setCurrentIndex(-1)
        self.add_button.setEnabled(False)
        self.remove_button.setEnabled(False)
        self.current_supports = None
        self.current_support = None
        self.current_character = None

    def _refresh_add_list(self):
        self.characters_widget.clear()
        if not self.target:
            return
        self.current_character = None
        self.add_button.setEnabled(False)
        unsupported_characters = self.service.get_unsupported_characters(self.target)
        self._add_characters_to_list(self.characters_widget, unsupported_characters)

    def _refresh_supports_list(self):
        self.supports_widget.clear()
        if not self.target:
            return
        self.current_supports = self.service.get_supports_for_character(self.target)
        self.current_support = None
        self.remove_button.setEnabled(False)
        supported_characters = self.service.get_supported_characters(self.target)
        self._add_characters_to_list(self.supports_widget, supported_characters)

    def _add_characters_to_list(self, target_list: QListWidget, characters: List[PropertyContainer]):
        for character in characters:
            self._add_character_to_list(target_list, character)

    @staticmethod
    def _add_character_to_list(target_list: QListWidget, character: PropertyContainer):
        item = QListWidgetItem()
        item.setText(character.get_display_name())
        item.setData(QtCore.Qt.UserRole, character)
        target_list.addItem(item)

    def _update_current_character(self, index: QtCore.QModelIndex):
        if not self.target:
            return
        item = self.characters_widget.itemFromIndex(index)
        if item:
            self.current_character = item.data(QtCore.Qt.UserRole)
            self.add_button.setEnabled(True)
            self.supports_widget.clearSelection()
            self.supports_widget.setCurrentIndex(QtCore.QModelIndex())
        else:
            self.current_character = None
            self.add_button.setEnabled(False)

    def _update_current_support(self, index: QtCore.QModelIndex):
        if not self.target or not self.current_supports:
            return
        if index.isValid():
            self.current_support = self.current_supports[index.row()]
            index = SUPPORT_TYPE_TO_INDEX[self.current_support.support_type]
            self.support_type_box.setCurrentIndex(index)
            self.support_type_box.setEnabled(True)
            self.remove_button.setEnabled(True)
            self.characters_widget.setCurrentIndex(QtCore.QModelIndex())
        else:
            self.current_support = None
            self.remove_button.setEnabled(False)
            self.support_type_box.setEnabled(False)

    def _on_support_type_changed(self, index: int):
        if not self.target or not self.current_support:
            return
        support_type = INDEX_TO_SUPPORT_TYPE[index]
        self.service.set_support_type(self.target, self.current_support, support_type)

    def _on_add_support_pressed(self):
        if not self.target or not self.current_character:
            return
        other_character = self.characters_widget.currentItem().data(QtCore.Qt.UserRole)
        support_type = INDEX_TO_SUPPORT_TYPE[0]  # Default to romantic.
        self.service.add_support_between_characters(self.target, other_character, support_type)
        self.characters_widget.takeItem(self.characters_widget.currentIndex().row())
        self._refresh_supports_list()
        self.supports_widget.setCurrentIndex(QtCore.QModelIndex())

    def _on_remove_support_pressed(self):
        if not self.target or not self.current_support:
            return
        self.service.remove_support(self.target, self.current_support)
        self.supports_widget.takeItem(self.supports_widget.currentIndex().row())
        self._refresh_add_list()
        self.characters_widget.setCurrentIndex(QtCore.QModelIndex())
        self.current_supports = self.service.get_supports_for_character(self.target)
