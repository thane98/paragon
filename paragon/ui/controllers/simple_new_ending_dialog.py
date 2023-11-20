import logging

from PySide6 import QtCore
from PySide6.QtWidgets import QDialogButtonBox, QStyle

from paragon.ui import utils
from paragon.ui.views.ui_simple_new_ending_dialog import Ui_SimpleNewEndingDialog


class SimpleNewEndingDialog(Ui_SimpleNewEndingDialog):
    def __init__(self, gd, service, characters_model, model, callback):
        super().__init__()
        self.model = model
        self.gd = gd
        self.service = service
        self.callback = callback

        self.char1_box.setModel(characters_model)
        self.char2_box.setModel(characters_model)
        self.char2_box.setCurrentIndex(-1)

        self._refresh_buttons()

        self.char1_box.currentIndexChanged.connect(self._refresh_buttons)
        self.char2_box.currentIndexChanged.connect(self._refresh_buttons)
        self.buttons.accepted.connect(self._on_ok)
        self.buttons.rejected.connect(self.reject)

    def _refresh_buttons(self):
        style = self.style()
        no_pixmap = style.standardPixmap(QStyle.SP_DialogNoButton)
        yes_pixmap = style.standardPixmap(QStyle.SP_DialogYesButton)

        char1 = self.char1_box.currentData(QtCore.Qt.UserRole)
        char2 = self.char2_box.currentData(QtCore.Qt.UserRole)
        valid = True
        if not char1:
            self.completion_graphic.setPixmap(no_pixmap)
            self.info_label.setText("Invalid: Must set character 1.")
            valid = False
        elif self.service.ending_exists(char1, char2):
            self.completion_graphic.setPixmap(no_pixmap)
            self.info_label.setText("Invalid: Ending already exists.")
        else:
            self.completion_graphic.setPixmap(yes_pixmap)
            self.info_label.setText("Valid: Everything checks out!")
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(valid)

    def _on_ok(self):
        try:
            self.service.create_ending(
                self.char1_box.currentData(QtCore.Qt.UserRole),
                self.char2_box.currentData(QtCore.Qt.UserRole),
            )
            self.callback(self.model.rowCount() - 1)
            self.accept()
        except:
            logging.exception("Encountered error while creating ending.")
            utils.error(self)
