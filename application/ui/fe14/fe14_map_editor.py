from PySide2.QtCore import QModelIndex
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QShortcut

from ui.views.ui_fe14_map_editor import Ui_FE14MapEditor


class FE14MapEditor(Ui_FE14MapEditor):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_terrain_mode = None

        self.deselect_shortcut = QShortcut(QKeySequence(QKeySequence.Cancel), self)
        self.add_item_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        self.delete_shortcut = QShortcut(QKeySequence(QKeySequence.Delete), self)
        self.copy_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        self.paste_shortcut = QShortcut(QKeySequence("Ctrl+V"), self)
        self.undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        self.redo_shortcut = QShortcut(QKeySequence("Ctrl+Shift+Z"), self)
        self.refresh_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)

        from .fe14_map_editor_dispos_controller import FE14MapEditorDisposController
        from .fe14_map_editor_terrain_controller import FE14MapEditorTerrainController
        self.dispos_controller = FE14MapEditorDisposController(self)
        self.terrain_controller = FE14MapEditorTerrainController(self)
        self.set_mode(False)

        self.toggle_mode_action.triggered.connect(self._toggle_mode)
        self.grid.coordinate_type_changed.connect(self._on_coordinate_type_changed)

    def update_chapter_data(self, chapter_data):
        self.grid.set_chapter_data(chapter_data)
        self.dispos_controller.update_chapter_data(chapter_data)
        self.terrain_controller.update_chapter_data(chapter_data)
        if not self.dispos_controller.active and chapter_data and chapter_data.terrain:
            self.set_mode(True)
        if not self.dispos_controller.active and not self.terrain_controller.active:
            self.setEnabled(False)
        else:
            self.setEnabled(True)

    def _toggle_mode(self):
        self.set_mode(not self.is_terrain_mode)

    def _on_selection_changed(self, index: QModelIndex):
        if self.is_terrain_mode:
            self.terrain_controller.update_selection(index)
        else:
            self.dispos_controller.update_selection(index)

    def _on_coordinate_type_changed(self):
        self.coordinate_type_label.setText("Coordinate type: " + self.grid.coordinate_key)

    def set_mode(self, is_terrain_mode: bool):
        self.is_terrain_mode = is_terrain_mode
        if self.is_terrain_mode:
            self.dispos_controller.set_active(False)
            self.terrain_controller.set_active(True)
            self.grid.transition_to_terrain_mode()
        else:
            self.terrain_controller.set_active(False)
            self.dispos_controller.set_active(True)
            self.grid.transition_to_dispos_mode()

    def show_spawn_pane(self, model):
        self.terrain_pane.hide()
        self.spawn_pane.show()
        self.model_view.setModel(model)
        self.model_view.selectionModel().currentChanged.connect(self._on_selection_changed)

    def show_terrain_pane(self, model):
        self.spawn_pane.hide()
        self.terrain_pane.show()
        self.model_view.setModel(model)
        self.model_view.selectionModel().currentChanged.connect(self._on_selection_changed)
