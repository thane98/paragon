import logging

from PySide6 import QtCore
from PySide6.QtWidgets import QDialogButtonBox, QStyle

from paragon.model.support_info import DialogueType
from paragon.ui import utils

from paragon.ui.views.ui_fe14_new_support_dialog import Ui_FE14NewSupportDialog


class FE14NewSupportDialog(Ui_FE14NewSupportDialog):
    def __init__(self, gd, models, service, supports_model, char1):
        super().__init__()

        self.char1 = char1
        self.service = service
        self.supports = supports_model.enumerate()
        self.supports_model = supports_model

        table, field_id = gd.table("characters")
        model = models.get(table, field_id)
        self.character.setModel(model)
        self.character.setCurrentIndex(-1)

        self.dialogue_type.setCurrentIndex(0)

        self._refresh()

        self.dialogue_type.currentIndexChanged.connect(self._refresh)
        self.character.currentIndexChanged.connect(self._refresh)
        self.buttons.accepted.connect(self._on_ok)
        self.buttons.rejected.connect(self.reject)

    def _refresh(self):
        style = self.style()
        no_pixmap = style.standardPixmap(QStyle.SP_DialogNoButton)
        yes_pixmap = style.standardPixmap(QStyle.SP_DialogYesButton)

        char = self.character.currentData(QtCore.Qt.UserRole)
        dialogue_type = self.dialogue_type.currentData(QtCore.Qt.UserRole)
        filled_out = char is not None and dialogue_type is not None
        if not filled_out:
            enabled = False
            self.user_info.setText("Invalid: Please select a character.")
            self.completion_graphic.setPixmap(no_pixmap)
        elif self.service.support_exists(char, dialogue_type, self.supports):
            enabled = False
            self.user_info.setText("Invalid: Support already exists.")
            self.completion_graphic.setPixmap(no_pixmap)
        else:
            enabled = True
            self.user_info.setText("Valid: Everything checks out!")
            self.completion_graphic.setPixmap(yes_pixmap)
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(enabled)

    def _on_ok(self):
        try:
            self.supports_model.add_support(
                self.char1,
                self.character.currentData(),
                DialogueType(self.dialogue_type.currentData()),
            )
            self.accept()
        except:
            logging.exception("Encountered error while creating support.")
            utils.error(self)
