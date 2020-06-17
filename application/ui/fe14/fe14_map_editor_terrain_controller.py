from typing import Optional

from PySide2 import QtCore
from PySide2.QtCore import QModelIndex

from model.fe14.chapter_data import ChapterData
from model.qt.tiles_model import TilesModel
from ui.fe14.fe14_map_editor import FE14MapEditor


class FE14MapEditorTerrainController:
    def __init__(self, map_editor: FE14MapEditor):
        self.view = map_editor
        self.error_dialog = None
        self.chapter_data: Optional[ChapterData] = None
        self.tiles_model: Optional[TilesModel] = None
        self.active = False
        self.set_active(self.active)

        self.view.add_tile_action.triggered.connect(self._add_tile)
        self.view.add_item_shortcut.activated.connect(self._add_tile)
        self.view.deselect_shortcut.activated.connect(self._deselect)

    def update_chapter_data(self, chapter_data: Optional[ChapterData]):
        self.chapter_data = chapter_data
        self.tiles_model = self.chapter_data.tiles_model if self.chapter_data else None
        self.view.terrain_pane.update_chapter_data(chapter_data)
        self.update_selection(QModelIndex())
        self.set_active(False)

    def update_selection(self, index: QModelIndex):
        if self.tiles_model and index.isValid():
            data = self.tiles_model.data(index, QtCore.Qt.UserRole)
            self.view.terrain_pane.update_tile_target(data)
            self.view.grid.selected_tile = data
        else:
            self.view.terrain_pane.update_tile_target(None)

    def set_active(self, active: bool):
        self.active = active and self.tiles_model
        if active:
            self.enable_actions_post_switch()
            self.view.show_terrain_pane(self.tiles_model)
        else:
            self.disable_all_actions()

    def enable_actions_post_switch(self):
        self.view.add_tile_action.setEnabled(True)

    def disable_all_actions(self):
        self.view.add_tile_action.setEnabled(False)

    def _add_tile(self):
        if self.active and self.tiles_model:
            self.tiles_model.add_tile()

    def _deselect(self):
        if self.active:
            self.view.model_view.setCurrentIndex(QModelIndex())
            self.view.terrain_pane.tile_form.update_target(None)
