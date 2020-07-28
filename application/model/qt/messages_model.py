from PySide2 import QtCore
from PySide2.QtGui import QStandardItemModel, QStandardItem

from model.message_archive import MessageArchive


class MessagesModel(QStandardItemModel):
    def __init__(self, message_archive: MessageArchive, parent=None):
        super().__init__(parent)
        self.message_archive = message_archive
        if message_archive:
            for message in self.message_archive.messages():
                item = self._create_item(message[0], message[1])
                self.appendRow(item)

    @staticmethod
    def _create_item(text, data):
        item = QStandardItem()
        item.setText(text)
        item.setData(data, QtCore.Qt.UserRole)
        return item

    def rename_message(self, old_name, new_name):
        message_value = self.message_archive.get_message(old_name)
        self.message_archive.erase_message(old_name)
        self.message_archive.insert_or_overwrite_message(new_name, message_value)
        for i in range(0, self.rowCount()):
            item = self.item(i, 0)
            if item.text() == old_name:
                item.setText(new_name)
                break

    def add_message(self, key):
        self.message_archive.insert_or_overwrite_message(key, "")
        self.appendRow(self._create_item(key, ""))

    def remove_message(self, key):
        self.message_archive.erase_message(key)
        for i in range(0, self.rowCount()):
            item = self.item(i, 0)
            if item.text() == key:
                self.removeRow(i)
                break

    def save_message(self, key, value):
        self.message_archive.insert_or_overwrite_message(key, value)
        for i in range(0, self.rowCount()):
            item = self.item(i, 0)
            if item.text() == key:
                item.setData(value, QtCore.Qt.UserRole)
                break
