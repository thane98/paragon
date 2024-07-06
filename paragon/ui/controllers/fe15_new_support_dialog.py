import logging

from PySide6 import QtCore
from PySide6.QtWidgets import QDialogButtonBox, QStyle
from paragon.ui import utils

from paragon.ui.views.ui_fe15_new_support_dialog import Ui_FE15NewSupportDialog


class FE15NewSupportDialog(Ui_FE15NewSupportDialog):
    def __init__(self, gd, models, service, supports_model, char):
        super().__init__()

        self.char = char
        self.service = service
        self.supports_model = supports_model

        table, field_id = gd.table("characters")
        model = models.get(table, field_id)
        self.character.setModel(model)
        self.character.setCurrentIndex(-1)

        self._refresh()

        self.character.currentIndexChanged.connect(self._refresh)
        self.buttons.accepted.connect(self._on_ok)
        self.buttons.rejected.connect(self.reject)

    def _refresh(self):
        style = self.style()
        no_pixmap = style.standardPixmap(QStyle.SP_DialogNoButton)
        yes_pixmap = style.standardPixmap(QStyle.SP_DialogYesButton)

        other_character = self.character.currentData(QtCore.Qt.UserRole)
        filled_out = other_character is not None
        if not filled_out:
            enabled = False
            self.user_info.setText("Invalid: Please select a character.")
            self.completion_graphic.setPixmap(no_pixmap)
        elif self.service.support_exists(self.char, other_character):
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
                self.char,
                self.character.currentData(),
                self.conditions_check_box.isChecked(),
                self.dialogue_check_box.isChecked(),
            )
            self.accept()
        except:
            logging.exception("Encountered error while creating support.")
            utils.error(self)
