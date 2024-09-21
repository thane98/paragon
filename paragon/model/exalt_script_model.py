import dataclasses
from pathlib import Path
from typing import Optional, Dict, Any

from PySide6 import QtCore
from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QStyle

NODE_ROLE = QtCore.Qt.ItemDataRole.UserRole
DIRECTORY_ROLE = QtCore.Qt.ItemDataRole.UserRole.value + 1
NODE_KIND_ROLE = QtCore.Qt.ItemDataRole.UserRole.value + 2


@dataclasses.dataclass
class ExaltScriptItemSummary:
    node: Optional[Any]
    node_kind: Optional[str]
    path: Optional[str]


class ExaltScriptModel(QStandardItemModel):
    def __init__(self, game_data, style: QStyle):
        super().__init__()

        self.game_data = game_data
        self.style = style
        self.dir_icon = self.style.standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        self.file_icon = self.style.standardIcon(QStyle.StandardPixmap.SP_FileIcon)

        self.scripts_root = self._create_dir_item("", "compile_target")
        self.scripts_root.setText("Scripts")
        self.user_libs_root = self._create_dir_item("", "user_library")
        self.user_libs_root.setText("Libraries")
        self.standard_libs_root = self._create_dir_item("", "standard_library")
        self.standard_libs_root.setText("Standard Library")

        self.scripts_dirs = {".": self.scripts_root}
        self.user_libs_dirs = {".": self.user_libs_root}
        self.standard_libs_dirs = {".": self.standard_libs_root}

        for node in self.game_data.get_script_nodes():
            if node.kind() == "compile_target":
                self._append_item(
                    self.scripts_dirs, Path(*Path(node.path).parts[2:]), node
                )
            elif node.kind() == "user_library":
                self._append_item(
                    self.user_libs_dirs, Path(*Path(node.path).parts[2:]), node
                )
            else:
                self._append_item(
                    self.standard_libs_dirs, Path(*Path(node.path).parts[1:]), node
                )

        self.invisibleRootItem().appendRow(self.scripts_root)
        self.invisibleRootItem().appendRow(self.user_libs_root)
        self.invisibleRootItem().appendRow(self.standard_libs_root)

    def _append_item(self, dirs: Dict[str, QStandardItem], path: Path, node):
        item = self._create_file_item(node)
        if parent_item := dirs.get(str(path.parent)):
            parent_item.appendRow(item)
        else:
            while True:
                path = path.parent
                if parent_item := dirs.get(str(path)):
                    parent_item.appendRow(item)
                    break
                else:
                    new_item = self._create_dir_item(str(path), node.kind())
                    new_item.appendRow(item)
                    dirs[str(path)] = new_item
                    item = new_item

    def _create_dir_item(self, path: str, node_kind: str) -> QStandardItem:
        item = QStandardItem()
        item.setText(Path(path).name)
        item.setIcon(self.dir_icon)
        item.setData(path, DIRECTORY_ROLE)
        item.setData(node_kind, NODE_KIND_ROLE)
        return item

    def _create_file_item(self, node) -> QStandardItem:
        item = QStandardItem()
        item.setText(Path(node.path).name)
        item.setIcon(self.file_icon)
        item.setData(node, NODE_ROLE)
        return item

    def data_at(self, index: QModelIndex) -> Optional[ExaltScriptItemSummary]:
        if item := self.itemFromIndex(index):
            return ExaltScriptItemSummary(
                item.data(NODE_ROLE),
                item.data(NODE_KIND_ROLE),
                item.data(DIRECTORY_ROLE),
            )
        else:
            return None

    def add_new_script_from_path(self, path: str):
        parent_path = Path(*Path(path).parts[1:-1])
        item = self.scripts_dirs.get(str(parent_path))
        if item:
            node = self.game_data.new_compiled_script(str(path))
            self._append_item(self.scripts_dirs, Path(*Path(path).parts[1:]), node)
            return node

    def add_new_script(self, parent_index: QModelIndex, file_name: str):
        data = self.data_at(parent_index)
        item = self.itemFromIndex(parent_index)
        if data and item:
            if data.node:
                raise Exception("expected directory node")
            path = Path(data.path).joinpath(file_name).with_suffix(".exl")
            if data.node_kind == "compile_target":
                node = self.game_data.new_compiled_script(str(path))
            else:
                node = self.game_data.new_source_only_script(str(path))
            item.appendRow(self._create_file_item(node))

    def add_new_dir(self, parent_index: QModelIndex, file_name: str):
        data = self.data_at(parent_index)
        item = self.itemFromIndex(parent_index)
        if data and item:
            if data.node:
                raise Exception("expected directory node")
            path = Path(data.path).joinpath(file_name)
            if data.node_kind == "compile_target":
                full_path = Path("exalt/scripts").joinpath(path)
                path_to_check = self.game_data.get_compiled_script_path(str(full_path))
                if self.game_data.exists(
                    str(full_path), False
                ) or self.game_data.exists(path_to_check, False):
                    return
            else:
                full_path = Path("exalt/libs").joinpath(path)
                if self.game_data.exists(str(full_path), False):
                    return
            self.game_data.create_dir(str(full_path), False)
            item.appendRow(self._create_dir_item(str(path), data.node_kind))

    def index_of(self, path: str, node_kind: str) -> Optional[QModelIndex]:
        if node_kind == "compile_target":
            return self._index_of_recursive(self.scripts_root, Path(path))
        elif node_kind == "user_library":
            return self._index_of_recursive(self.user_libs_root, Path(path))
        else:
            return self._index_of_recursive(self.standard_libs_root, Path(path))

    def _index_of_recursive(
        self, item: QStandardItem, path: Path
    ) -> Optional[QModelIndex]:
        data = item.data(NODE_ROLE)
        if data and Path(data.path) == path:
            return self.indexFromItem(item)
        else:
            for i in range(0, item.rowCount()):
                if index := self._index_of_recursive(item.child(i), path):
                    return index
        return None
