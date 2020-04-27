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

    def remove_voice_set(self, voice_set_label: str):
        self.service.remove_voice_set(voice_set_label)
        self.beginResetModel()
        self.endResetModel()

    def create_voice_set(self, voice_set_label: str):
        self.service.create_voice_set(voice_set_label)
        self.beginResetModel()
        self.endResetModel()


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

    def insertRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        self.beginInsertRows(parent, row, row + count)
        for _ in range(0, count):
            new_entry = self.service.append_entry_to_voice_set(self.voice_set_label)
            self.entries.append(new_entry)
        self.endInsertRows()
        return True

    def removeRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        if row not in range(0, len(self.entries)) or row + count not in range(0, len(self.entries) + 1):
            return False

        self.beginRemoveRows(parent, row, row + count)
        self.service.remove_entry_from_voice_set(self.voice_set_label, row)
        self.endRemoveRows()
        return True

    def remove_entry(self, entry: PropertyContainer):
        for i in range(0, len(self.entries)):
            if self.entries[i] == entry:
                self.removeRow(i)
                del self.entries[i]
                return
        raise Exception

    def save_entry(self, entry: PropertyContainer):
        for i in range(0, len(self.entries)):
            if self.entries[i] == entry:
                self.service.save_entry(self.voice_set_label, entry, i)
                return
        raise Exception

    def synchronize_tags(self, source: PropertyContainer):
        source_tag = source["Tag"]
        for i in range(0, len(self.entries)):
            entry = self.entries[i]
            if entry != source:
                source_tag.copy_to(entry["Tag"])
                self.service.save_entry(self.voice_set_label, entry, i)
