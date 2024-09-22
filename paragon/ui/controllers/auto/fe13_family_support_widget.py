import logging
from typing import Optional, List

from PySide6 import QtCore
from PySide6.QtWidgets import QListWidgetItem

from paragon.core.services.fe13_supports import FE13FamilySupport
from paragon.model.game import Game
from paragon.ui import utils
from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget
from paragon.ui.controllers.dialogue_editor import DialogueEditor
from paragon.ui.controllers.fe13_new_family_support_dialog import FE13NewFamilySupportDialog
from paragon.ui.views.ui_fe13_family_support_widget import Ui_FE13FamilySupportWidget


class FE13FamilySupportWidget(AbstractAutoWidget, Ui_FE13FamilySupportWidget):
    def __init__(self, state):
        AbstractAutoWidget.__init__(self, state)
        Ui_FE13FamilySupportWidget.__init__(self)

        self.rid = None
        self.supports = self.gs.supports
        self.editors = {}
        self.new_dialog = None

        self.supports_list.currentItemChanged.connect(self._update_buttons)
        self.new_button.clicked.connect(self._on_new)
        self.open_button.clicked.connect(self._on_open)

        self._update_buttons()

    def set_target(self, rid):
        self.rid = rid
        self.supports_list.clear()
        self.supports_list.clearSelection()
        self._update_buttons()

        if self.rid:
            supports: Optional[List[FE13FamilySupport]] = self.supports.get_supports(
                self.rid
            )
            if supports:
                for support in supports:
                    text = f"{self.data.display(support.char1)} x {self.data.display(support.char2)} ({support.support_type.value})"
                    item = QListWidgetItem(text)
                    item.setData(QtCore.Qt.ItemDataRole.UserRole, support)
                    self.supports_list.addItem(item)

    def _update_buttons(self):
        self.open_button.setEnabled(self.supports_list.currentItem() is not None)
        self.new_button.setEnabled(self.rid is not None)

    def _on_new(self):
        self.new_dialog = FE13NewFamilySupportDialog(self.data, self.gs.models, self.gs.supports, self.supports_list, self.rid)
        self.new_dialog.show()

    def _on_open(self):
        item = self.supports_list.currentItem()
        if not item:
            return
        info: FE13FamilySupport = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if not info:
            return
        path = info.path
        if path in self.editors:
            self.editors[path].show()
            return
        try:
            editor = DialogueEditor(
                self.data, self.gs.dialogue, self.gs.sprite_animation, Game.FE13
            )
            editor.set_archive(info.path, info.localized)
            self.editors[info.path] = editor
            editor.show()
        except:
            logging.exception("Failed to open support.")
            utils.error(self)
