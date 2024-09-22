import logging

from PySide6 import QtCore
from PySide6.QtWidgets import QDialogButtonBox, QStyle, QListWidgetItem

from paragon.core.services.fe13_supports import FE13FamilySupportType
from paragon.ui import utils
from paragon.ui.views.ui_fe13_new_family_support_dialog import (
    Ui_FE13NewFamilySupportDialog,
)


class FE13NewFamilySupportDialog(Ui_FE13NewFamilySupportDialog):
    def __init__(self, gd, models, service, support_widget, char1):
        super().__init__()

        self.gd = gd
        self.char1 = char1
        self.service = service
        self.support_widget = support_widget

        table, field_id = gd.table("characters")
        model = models.get(table, field_id)
        self.character.setModel(model)
        self.character.setCurrentIndex(-1)
        self.dialogue_type.setCurrentIndex(0)

        self._refresh()

        self.character.currentIndexChanged.connect(self._refresh)
        self.dialogue_type.currentIndexChanged.connect(self._refresh)
        self.buttons.accepted.connect(self._on_ok)
        self.buttons.rejected.connect(self.reject)

    def _refresh(self):
        style = self.style()
        no_pixmap = style.standardPixmap(QStyle.StandardPixmap.SP_DialogNoButton)
        yes_pixmap = style.standardPixmap(QStyle.StandardPixmap.SP_DialogYesButton)

        char2 = self.character.currentData(QtCore.Qt.ItemDataRole.UserRole)
        dialogue_type = FE13FamilySupportType(self.dialogue_type.currentData())
        filled_out = char2 is not None
        if not filled_out:
            enabled = False
            self.user_info.setText("Invalid: Please select a character.")
            self.completion_graphic.setPixmap(no_pixmap)
        elif self.service.family_support_exists(self.char1, char2, dialogue_type):
            enabled = False
            self.user_info.setText("Invalid: Support already exists.")
            self.completion_graphic.setPixmap(no_pixmap)
        else:
            enabled = True
            self.user_info.setText("Valid: Everything checks out!")
            self.completion_graphic.setPixmap(yes_pixmap)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(enabled)

    def _on_ok(self):
        try:
            support = self.service.add_support(
                self.char1,
                self.character.currentData(),
                FE13FamilySupportType(self.dialogue_type.currentData()),
            )

            text = f"{self.gd.display(support.char1)} x {self.gd.display(support.char2)} ({support.support_type.value})"
            item = QListWidgetItem(text)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, support)
            self.support_widget.addItem(item)

            self.accept()
        except:
            logging.exception("Encountered error while creating support.")
            utils.error(self)
