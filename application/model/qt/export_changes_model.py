from typing import Any

from PySide2 import QtCore
from PySide2.QtGui import QStandardItemModel, QStandardItem

from core.export_capabilities import ExportCapabilities
from services.service_locator import locator

_GET_NODE_ROLE = QtCore.Qt.UserRole
_HAS_LOADED_DATA_ROLE = QtCore.Qt.UserRole + 1
_EXPANDABLE_ROLE = QtCore.Qt.UserRole + 2
_CAPABILITIES_ROLE = QtCore.Qt.UserRole + 3


def _create_expandable_item(data, text: str) -> QStandardItem:
    item = _create_standard_item(data, text)
    item.setText(text)
    item.setData(data, _GET_NODE_ROLE)
    item.setData(False, _HAS_LOADED_DATA_ROLE)
    item.setData(True, _EXPANDABLE_ROLE)
    return item


def _create_standard_item(data, text: str) -> QStandardItem:
    item = QStandardItem()
    capabilities: ExportCapabilities = data.export_capabilities()
    if capabilities.is_selectable():
        item.setCheckable(True)
    item.setText(text)
    item.setData(data, _GET_NODE_ROLE)
    item.setData(capabilities, _CAPABILITIES_ROLE)
    return item


class ExportChangesModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        module_item = _create_expandable_item(locator.get_scoped("ModuleService"), "Modules")
        common_modules_item = _create_expandable_item(locator.get_scoped("CommonModuleService"), "Common Modules")
        services_item = _create_expandable_item(locator.get_scoped("DedicatedEditorsService"), "Services")
        self.appendRow(module_item)
        self.appendRow(common_modules_item)
        self.appendRow(services_item)

        self.itemChanged.connect(self._update_check_state)

    def hasChildren(self, parent: QtCore.QModelIndex = ...) -> bool:
        if parent.isValid() and self.data(parent, _EXPANDABLE_ROLE):
            return True
        return super().hasChildren(parent)

    def update_data_for_index(self, index: QtCore.QModelIndex):
        item = self.itemFromIndex(index)
        self._update_data_for_item(item)

    @staticmethod
    def _update_data_for_item(item: QStandardItem):
        if not item.data(_EXPANDABLE_ROLE):
            return
        if not item.data(_HAS_LOADED_DATA_ROLE):
            node = item.data(_GET_NODE_ROLE)
            for child, name in node.children():
                if hasattr(child, "children"):
                    child_item = _create_expandable_item(child, name)
                else:
                    child_item = _create_standard_item(child, name)
                item.appendRow(child_item)
            item.setData(True, _HAS_LOADED_DATA_ROLE)

    def export_selected_items(self):
        root = self.invisibleRootItem()
        return self._recursive_export_selected_items(root)

    def _recursive_export_selected_items(self, item: QStandardItem) -> Any:
        self._ensure_loading_of_children(item)
        if item.rowCount() == 0 and item.checkState():
            node = item.data(_GET_NODE_ROLE)
            return node.export()
        else:
            result = {}
            for i in range(0, item.rowCount()):
                child = item.child(i)
                child_data = self._recursive_export_selected_items(child)
                if child_data != {}:
                    result[child.text()] = child_data

            if result and self._is_create_new_selection(item):
                result["__CREATE_NEW__"] = item.checkState() != QtCore.Qt.Unchecked
            return result

    @staticmethod
    def _is_create_new_selection(item: QStandardItem):
        capabilities: ExportCapabilities = item.data(_CAPABILITIES_ROLE)
        return item.checkState() == QtCore.Qt.Checked and capabilities.is_appendable()

    def _ensure_loading_of_children(self, item: QStandardItem):
        if not item.checkState():
            return
        self._update_data_for_item(item)

    def _update_check_state(self, item: QStandardItem):
        capabilities: ExportCapabilities = item.data(_CAPABILITIES_ROLE)
        if capabilities.is_selectable():
            new_state = item.checkState()
            self.blockSignals(True)
            for i in range(0, item.rowCount()):
                self._recursive_update_check_state(item.child(i), new_state)
            self.blockSignals(False)

    def _recursive_update_check_state(self, item: QStandardItem, new_state: QtCore.Qt.CheckState):
        if item.rowCount() != 0:
            for i in range(0, item.rowCount()):
                self._recursive_update_check_state(item.child(i), new_state)
        item.setCheckState(new_state)
        item.setEnabled(new_state != QtCore.Qt.Checked)
