from typing import Any

from PySide2 import QtCore
from PySide2.QtGui import QStandardItemModel, QStandardItem

from core.export_capabilities import ExportCapabilities
from services.service_locator import locator

_GET_NODE_ROLE = QtCore.Qt.UserRole
_HAS_LOADED_DATA_ROLE = QtCore.Qt.UserRole + 1
_EXPANDABLE_ROLE = QtCore.Qt.UserRole + 2
_CAPABILITIES_ROLE = QtCore.Qt.UserRole + 3
_KEY_ROLE = QtCore.Qt.UserRole + 4


def _create_expandable_item(data, text: str, key: str) -> QStandardItem:
    item = _create_standard_item(data, text, key)
    item.setText(text)
    item.setData(data, _GET_NODE_ROLE)
    item.setData(False, _HAS_LOADED_DATA_ROLE)
    item.setData(True, _EXPANDABLE_ROLE)
    return item


def _create_standard_item(data, text: str, key: str) -> QStandardItem:
    item = QStandardItem()
    capabilities: ExportCapabilities = data.export_capabilities()
    if capabilities.is_selectable():
        item.setCheckable(True)
    item.setText(text)
    item.setData(data, _GET_NODE_ROLE)
    item.setData(capabilities, _CAPABILITIES_ROLE)
    item.setData(key, _KEY_ROLE)
    return item


class ExportChangesModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        module_item = _create_expandable_item(locator.get_scoped("ModuleService"), "Modules", "Modules")
        common_modules_item = _create_expandable_item(
            locator.get_scoped("CommonModuleService"),
            "Common Modules",
            "Common Modules"
        )
        services_item = _create_expandable_item(
            locator.get_scoped("DedicatedEditorsService"),
            "Services",
            "Services"
        )
        self.appendRow(module_item)
        self.appendRow(common_modules_item)
        self.appendRow(services_item)

        self.itemChanged.connect(self._update_check_state)
        self.restore_selections_from_project()

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
            for child, name, key in node.children():
                if hasattr(child, "children"):
                    child_item = _create_expandable_item(child, name, key)
                else:
                    child_item = _create_standard_item(child, name, key)
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
                    result[child.data(_KEY_ROLE)] = child_data

            if result and self._is_create_new_selection(item):
                result["__CREATE_NEW__"] = item.checkState() != QtCore.Qt.Unchecked
            return result

    def restore_selections_from_project(self):
        project = locator.get_scoped("Driver").get_project()
        if project.export_selections and locator.get_static("SettingsService").get_remember_exports():
            self._recursive_restore_selections_from_project(self.invisibleRootItem(), project.export_selections)

    def _recursive_restore_selections_from_project(self, item: QStandardItem, selections):
        if item.rowCount() == 0 and not item.data(_EXPANDABLE_ROLE) or not isinstance(selections, dict):
            return
        else:
            for i in range(0, item.rowCount()):
                child = item.child(i)
                child_key = child.data(_KEY_ROLE)
                child_capabilities = child.data(_CAPABILITIES_ROLE)
                if child_key in selections:
                    self._update_data_for_item(child)
                    if child_capabilities.is_selectable():
                        child.setCheckState(QtCore.Qt.Checked)
                    self._recursive_restore_selections_from_project(child, selections[child_key])

    def save_selected_items_tree(self):
        project = locator.get_scoped("Driver").get_project()
        if locator.get_static("SettingsService").get_remember_exports():
            project.export_selections = self._recursive_get_selected_items_tree(self.invisibleRootItem())

    def _recursive_get_selected_items_tree(self, item: QStandardItem):
        if item.rowCount() == 0 and item.checkState() == QtCore.Qt.Checked:
            return item.data(_KEY_ROLE)
        elif item.rowCount() > 0:
            result = {}
            for i in range(0, item.rowCount()):
                child = item.child(i)
                selected_children = self._recursive_get_selected_items_tree(child)
                if selected_children:
                    result[child.data(_KEY_ROLE)] = selected_children
            return result
        else:
            return None

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
