import logging

from PySide6 import QtCore

from paragon.core.services.fe15_supports_model import FE15SupportsModel
from paragon.model.game import Game
from paragon.ui import utils
from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget
from paragon.ui.controllers.dialogue_editor import DialogueEditor
from paragon.ui.controllers.fe15_new_support_dialog import FE15NewSupportDialog
from paragon.ui.views.ui_fe15_support_widget import Ui_FE15SupportWidget


class FE15SupportWidget(AbstractAutoWidget, Ui_FE15SupportWidget):
    def __init__(self, state):
        AbstractAutoWidget.__init__(self, state)
        Ui_FE15SupportWidget.__init__(self)

        self.conditions_widget = state.generator.generate_for_type(
            "SupportConditionsDataItem"
        )
        self.conditions_box.layout().addWidget(self.conditions_widget)
        self.effects_widget = state.generator.generate_for_type("SupportEffectDataItem")
        self.content_layout.addWidget(self.effects_widget)

        self.conditions_widget.gen_widgets["support_conditions_character"].setEnabled(
            False
        )
        self.effects_widget.gen_widgets["support_effects_character"].setEnabled(False)

        self.service = self.gs.supports
        self.model = FE15SupportsModel(self.data, self.gs.supports)
        self.rid = None
        self.dialogue_editors = {}
        self.new_dialog = None

        self.supports_list.setModel(self.model)
        self._update_buttons()

        self.supports_list.selectionModel().currentChanged.connect(
            self._on_current_changed
        )
        self.new_button.clicked.connect(self._on_new)
        self.delete_button.clicked.connect(self._on_delete)
        self.open_button.clicked.connect(self._on_open)
        self.add_conditions_button.clicked.connect(self._on_add_conditions)
        self.add_dialogue_button.clicked.connect(self._on_add_dialogue)

    def set_target(self, rid):
        self.rid = rid
        self.model.set_character(rid)
        self._update_buttons()

    def _on_current_changed(self):
        self._update_buttons()
        info = self.model.data(self.supports_list.currentIndex(), QtCore.Qt.UserRole)
        if not info:
            self.conditions_widget.set_target(None)
            self.effects_widget.set_target(None)
        else:
            self.conditions_widget.set_target(info.conditions)
            self.effects_widget.set_target(info.effects)
        self.conditions_widget.gen_widgets["support_conditions_character"].setEnabled(
            False
        )
        self.effects_widget.gen_widgets["support_effects_character"].setEnabled(False)

    def _update_buttons(self):
        data = self.model.data(self.supports_list.currentIndex(), QtCore.Qt.UserRole)
        valid = data is not None
        self.new_button.setEnabled(self.rid is not None)
        self.delete_button.setEnabled(valid)
        self.open_button.setEnabled(valid and data.archive_path is not None)
        self.add_conditions_button.setEnabled(valid and data.conditions is None)
        self.add_dialogue_button.setEnabled(valid and data.archive_path is None)

    def _on_new(self):
        if not self.rid:
            return
        self.new_dialog = FE15NewSupportDialog(
            self.data, self.gs.models, self.service, self.model, self.rid
        )
        self.new_dialog.show()

    def _on_delete(self):
        if not self.rid or not self.supports_list.currentIndex().isValid():
            return
        self.model.delete_support(self.supports_list.currentIndex())

    def _on_open(self):
        info = self.model.data(self.supports_list.currentIndex(), QtCore.Qt.UserRole)
        if not info:
            return
        archive_path = info.archive_path
        if archive_path in self.dialogue_editors:
            self.dialogue_editors[archive_path].show()
            return
        try:
            editor = DialogueEditor(
                self.data,
                self.gs.dialogue,
                self.gs.sprite_animation,
                Game.FE15,
            )
            editor.set_archive(archive_path, True)
            self.dialogue_editors[archive_path] = editor
            editor.show()
        except:
            logging.exception("Failed to open support.")
            utils.error(self)

    def _on_add_conditions(self):
        info = self.model.data(self.supports_list.currentIndex(), QtCore.Qt.UserRole)
        if not info:
            return
        try:
            self.service.add_conditions_to_support(info)
            self._on_current_changed()
        except:
            logging.exception("Failed to add conditions to support.")
            utils.error(self)

    def _on_add_dialogue(self):
        info = self.model.data(self.supports_list.currentIndex(), QtCore.Qt.UserRole)
        if not info:
            return
        try:
            self.service.add_message_archive_to_support(info)
            self._on_current_changed()
        except:
            logging.exception("Failed to add conditions to support.")
            utils.error(self)
