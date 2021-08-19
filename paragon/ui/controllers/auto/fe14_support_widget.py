import logging

from PySide2 import QtCore
from paragon.model.support_info import DialogueType

from paragon.model.support_sort_mode import SupportSortMode
from paragon.ui import utils

from paragon.model.game import Game

from paragon.model.supports_model import SupportsModel
from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget
from paragon.ui.controllers.fe14_new_support_dialog import FE14NewSupportDialog
from paragon.ui.controllers.fe14_support_dialogue_editor import FE14SupportDialogueEditor

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
        self.support_type_box = self.support_form.gen_widgets["support_type"]
        self.layout().addWidget(self.support_form)

        self.model = SupportsModel(self.data, state.game_state.supports)
        self.supports_list.setModel(self.model)

        self.supports_list.selectionModel().currentChanged.connect(
            self._on_current_changed
        )
        self.new_button.clicked.connect(self._on_new)
        self.delete_button.clicked.connect(self._on_delete)
        self.open_button.clicked.connect(self._on_open)
        self.support_type_box.currentIndexChanged.connect(self._on_support_type_changed)

        self._update_buttons()

    def set_target(self, rid):
        self.rid = rid
        self.model.set_character(rid)
        self.supports_list.clearSelection()
        self._update_buttons()

    def _update_buttons(self):
        data = self.model.data(self.supports_list.currentIndex(), QtCore.Qt.UserRole)
        valid = data is not None
        self.new_button.setEnabled(self.rid is not None)
        self.delete_button.setEnabled(valid and data.dialogue_type == DialogueType.STANDARD)
        self.open_button.setEnabled(valid)

    def _on_current_changed(self):
        self._update_buttons()
        info = self.model.data(self.supports_list.currentIndex(), QtCore.Qt.UserRole)
        if not info:
            self.support_form.set_target(None)
        else:
            self.support_form.set_target(info.support)

    def _on_support_type_changed(self):
        if info := self.model.data(self.supports_list.currentIndex(), QtCore.Qt.UserRole):
            value = self.support_type_box.currentData()
            self.supports.set_type_for_inverse_support(info, value)

    def _on_new(self):
        self.new_dialog = FE14NewSupportDialog(
            self.data, self.gs.models, self.supports, self.model, self.rid
        )
        self.new_dialog.show()

    def _on_delete(self):
        try:
            self.model.delete_support(self.supports_list.currentIndex())
        except:
            logging.exception("Failed to delete support.")
            utils.error(self)

    def _on_open(self):
        info = self.model.data(self.supports_list.currentIndex(), QtCore.Qt.UserRole)
        if not info:
            return
        path = info.dialogue_path
        if path in self.editors:
            self.editors[path].show()
            return
        try:
            editor = FE14SupportDialogueEditor(
                self.data, self.gs.dialogue, self.gs.sprite_animation, Game.FE14
            )
            editor.set_archive(info.dialogue_path, not info.already_localized)
            self.editors[info.dialogue_path] = editor
            editor.show()
        except:
            logging.exception("Failed to open support.")
            utils.error(self)
