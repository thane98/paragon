import os
from typing import List

from PySide2.QtGui import QStandardItemModel, QStandardItem

from module.module import Module


class ModuleModel(QStandardItemModel):
    def __init__(self, modules: List[Module], parent=None):
        super().__init__(parent)
        self.modules: List[Module] = modules
        self._populate_model()

    def _populate_model(self):
        self.clear()
        category_tree = self._get_categories_tree(self.modules)
        for key, value in category_tree.items():
            child = self._build_item_for_tree_node(key, value)
            self.appendRow(child)

    def _build_item_for_tree_node(self, key, node):
        item = QStandardItem()
        if type(node) == dict:
            # Node is a category.
            item.setText(key)
            for child_key, value in node.items():
                child = self._build_item_for_tree_node(child_key, value)
                item.appendRow(child)
        else:
            # Node is a module.
            item.setText(key)
            item.setData(node)
        return item

    @staticmethod
    def _get_categories_tree(modules: List[Module]):
        categories_tree = {}
        for module in modules:
            cur_node = categories_tree
            categories = os.path.split(os.path.normpath(module.parent_path_from_base))
            for category in categories:
                if not category:
                    continue
                if category not in cur_node:
                    cur_node[category] = {}
                cur_node = cur_node[category]
            cur_node[module.name] = module
        return categories_tree
