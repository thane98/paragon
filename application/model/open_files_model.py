import logging
from typing import Any

from PySide2 import QtCore
from PySide2.QtCore import QAbstractListModel, QModelIndex
from services.service_locator import locator


class OpenFilesModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.open_files_services = locator.get_scoped("OpenFilesService")

    def can_close(self, index):
        (_, value) = self._get_elem(index)
        module_service = locator.get_scoped("ModuleService")
        return module_service.is_archive_used_by_module(value.file)

    def close(self, index):
        (key, value) = self._get_elem(index)
        logging.info("Closing file " + key)
        archive = value.file

        self.beginRemoveRows(QModelIndex(), index, index + 1)
        self.driver.close_archive(archive)
        self.endRemoveRows()

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.open_files_services.open_files)

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if not index.isValid():
            return None
        (key, value) = self._get_elem(index.row())
        if role == QtCore.Qt.DisplayRole:
            return key
        return None

    def _get_elem(self, index):
        i = 0
        for elem in self.open_files_services.open_files.items():
            if i == index:
                return elem
            i += 1
        return None
