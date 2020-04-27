from typing import Any, List

from PySide2 import QtCore
from PySide2.QtCore import QAbstractListModel, QModelIndex

from module.properties.property_container import PropertyContainer
from services.service_locator import locator


class VoiceSetModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = locator.get_scoped("SoundService")

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.service.voice_set_labels)

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if not index.isValid():
            return None

        voice_set_label = self.service.voice_set_labels[index.row()]
        if role == QtCore.Qt.DisplayRole:
            return voice_set_label
        if role == QtCore.Qt.UserRole:
            return self.service.get_voice_set(voice_set_label)
        return None


class VoiceSetEntriesModel(QAbstractListModel):
    def __init__(self, voice_set_label: str, entries: List[PropertyContainer], parent=None):
        super().__init__(parent)
        self.voice_set_label = voice_set_label
        self.entries = entries
        self.service = locator.get_scoped("SoundService")

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.entries)

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if not index.isValid():
            return None

        entry = self.entries[index.row()]
        if role == QtCore.Qt.DisplayRole:
            return entry["Name"].value
        if role == QtCore.Qt.UserRole:
            return entry
        return None

    def save_entry(self, entry: PropertyContainer):
        for i in range(0, len(self.entries)):
            if self.entries[i] == entry:
                self.service.save_entry(self.voice_set_label, entry, i)
                return
        raise Exception
