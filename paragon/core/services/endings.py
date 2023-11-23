import logging
from typing import Optional

from PySide6 import QtCore
from PySide6.QtGui import QFont, QStandardItemModel, QStandardItem

from paragon.model.ending import Ending


class Endings:
    def __init__(self, gd, portraits):
        self.gd = gd
        self.portraits = portraits
        self._loaded_assets = False
        self._created_model = False
        self._assets = {}
        self._model = None

    def model(self):
        if not self._created_model:
            self._model = self._create_model()
            self._created_model = True
        return self._model

    def archive(self):
        raise NotImplementedError

    def parse_key(self, key: str) -> Optional[Ending]:
        return self._parse_key(key, key.split("_"))

    def font(self) -> QFont:
        font = QFont("FOT-Chiaro Std B")
        font.setPixelSize(15)
        return font

    def assets(self):
        if not self._loaded_assets:
            try:
                self._assets = self._load_assets()
            except:
                logging.exception("Failed to load ending assets.")
            self._loaded_assets = True
        return self._assets

    def update_ending(self, key, value):
        text = value.replace("\n", "\\n")
        text = text.replace("\r", "")
        self.gd.set_message(self.archive(), True, key, text)

    def create_ending(self, char1, char2):
        ending = self._create_ending(char1, char2)
        item = QStandardItem()
        item.setText(ending.display())
        item.setData(ending, QtCore.Qt.UserRole)
        self.model().appendRow(item)

    def ending_exists(self, char1, char2) -> bool:
        return bool(self.get_ending(char1, char2))

    def get_ending(self, char1, char2) -> Optional[Ending]:
        model = self.model()
        for row in range(0, model.rowCount()):
            item = model.item(row)
            ending = item.data(QtCore.Qt.UserRole)
            if (
                char1 == ending.char1
                and char2 == ending.char2
                or char2 == ending.char1
                and char1 == ending.char2
            ):
                return ending
        return None

    def _create_model(self) -> QStandardItemModel:
        raise NotImplementedError

    def _create_ending(self, char1, char2) -> Ending:
        raise NotImplementedError

    def get_portraits_for_ending(self, ending: Ending):
        raise NotImplementedError

    def _parse_key(self, key, parts):
        raise NotImplementedError

    def _load_assets(self):
        raise NotImplementedError
