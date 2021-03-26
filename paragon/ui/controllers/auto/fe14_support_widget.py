import logging

from PySide2 import QtCore
from PySide2.QtCore import QSortFilterProxyModel, QModelIndex
from paragon.model.support_info import DialogueType

from paragon.model.support_sort_mode import SupportSortMode
from paragon.ui import utils

from paragon.model.game import Game

from paragon.ui.controllers.dialogue_editor import DialogueEditor

from paragon.model.supports_model import SupportsModel
from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget
from paragon.ui.controllers.fe14_new_support_dialog import FE14NewSupportDialog

from paragon.ui.views.ui_fe14_support_widget import Ui_FE14SupportWidget


class FE14SupportWidget(AbstractAutoWidget, Ui_FE14SupportWidget):
    def __init__(self, state):
        AbstractAutoWidget.__init__(self, state)
        Ui_FE14SupportWidget.__init__(self)

        self.rid = None
        self.supports = self.gs.supports
        self.editors = {}
        self.new_dialog = None
        self.sort_mode = SupportSortMode(0)

        gen = state.generator
        self.support_form = gen.generate_for_type("Support")
        self.layout().addWidget(self.support_form)

        self.model = SupportsModel(self.data, state.game_state.supports)
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setDynamicSortFilter(True)
        self.supports_list.setModel(self.proxy_model)

        self.supports_list.selectionModel().currentChanged.connect(
            self._on_current_changed
        )
        self.new_button.clicked.connect(self._on_new)
        self.delete_button.clicked.connect(self._on_delete)
        self.open_button.clicked.connect(self._on_open)
        self.sort_box.currentIndexChanged.connect(self._on_sort_mode_changed)

        self.sort_box.setCurrentIndex(0)
        self._update_buttons()

    def set_target(self, rid):
        self.rid = rid
        self.model.set_character(rid)
        self.supports_list.clearSelection()
        self._update_buttons()

    def _update_buttons(self):
        data = self.proxy_model.data(self.supports_list.currentIndex(), QtCore.Qt.UserRole)
        valid = data is not None
        self.new_button.setEnabled(self.rid is not None)
        self.delete_button.setEnabled(valid and data.dialogue_type == DialogueType.STANDARD)
        self.open_button.setEnabled(valid)

    def _on_sort_mode_changed(self):
        self.sort_mode = SupportSortMode(self.sort_box.currentIndex())
        if self.sort_mode == SupportSortMode.NAME:
            self.proxy_model.setSortRole(QtCore.Qt.DisplayRole)
        else:
            self.proxy_model.setSortRole(SupportsModel.SORT_BY_ID_ROLE)
        self.proxy_model.sort(0)
        self.supports_list.clearSelection()
        self.supports_list.setCurrentIndex(QModelIndex())

    def _on_current_changed(self):
        self._update_buttons()
        info = self.proxy_model.data(self.supports_list.currentIndex(), QtCore.Qt.UserRole)
        if not info:
            self.support_form.set_target(None)
        else:
            self.support_form.set_target(info.support)

    def _on_new(self):
        self.new_dialog = FE14NewSupportDialog(
            self.data, self.gs.models, self.supports, self.model, self.rid
        )
        self.new_dialog.show()

    def _on_delete(self):
        try:
            index = self.supports_list.currentIndex()
            self.model.delete_support(self.proxy_model.mapToSource(index))
        except:
            logging.exception("Failed to delete support.")
            utils.error(self)

    def _on_open(self):
        info = self.proxy_model.data(self.supports_list.currentIndex(), QtCore.Qt.UserRole)
        if not info:
            return
        path = info.dialogue_path
        if path in self.editors:
            self.editors[path].show()
            return
        try:
            if not self.data.file_exists(path, True):
                self.supports.create_dialogue_archive(
                    info.char1, info.char2, info.dialogue_type
                )
            editor = DialogueEditor(
                self.data, self.gs.dialogue, self.gs.sprite_animation, Game.FE14
            )
            editor.set_archive(info.dialogue_path, True)
            self.editors[info.dialogue_path] = editor
            editor.show()
        except:
            logging.exception("Failed to open support.")
            utils.error(self)
