from PySide2 import QtGui, QtCore
from PySide2.QtCore import QModelIndex
from PySide2.QtWidgets import QWidget, QTreeView, QSplitter, QVBoxLayout, QFormLayout, QScrollArea, QLabel, QCheckBox

from model import fe14
from model.fe14 import dispo
from model.fe14.dispo_model import DisposModel
from model.fe14.terrain import Terrain
from model.fe14.tiles_model import TilesModel
from ui.map_grid import MapGrid


def _create_form(template):
    editors = []
    layout = QFormLayout()
    for (key, prop) in template.items():
        label = QLabel(key)
        editor = prop.create_editor()
        if editor:
            editors.append(editor)
            layout.addRow(label, editor)
    form_widget = QWidget()
    form_widget.setLayout(layout)
    scroll_area = QScrollArea()
    scroll_area.setWidget(form_widget)
    scroll_area.setWidgetResizable(True)
    return scroll_area, editors


def _create_editor_for_property(prop, layout, editor_list):
    editor = prop.create_editor()
    if editor:
        label = QLabel(prop.name)
        layout.addRow(label, editor)
        editor_list.append(editor)


def _create_terrain_form():
    terrain = Terrain()
    persistent_form = QFormLayout()
    persistent_editors = []
    _create_editor_for_property(terrain.map_model, persistent_form, persistent_editors)
    _create_editor_for_property(terrain.map_size_x, persistent_form, persistent_editors)
    _create_editor_for_property(terrain.map_size_y, persistent_form, persistent_editors)
    _create_editor_for_property(terrain.border_size_x, persistent_form, persistent_editors)
    _create_editor_for_property(terrain.border_size_y, persistent_form, persistent_editors)
    _create_editor_for_property(terrain.trimmed_size_x, persistent_form, persistent_editors)
    _create_editor_for_property(terrain.trimmed_size_y, persistent_form, persistent_editors)
    (tile_form, tile_editors) = _create_form(fe14.terrain.TILE_TEMPLATE)
    tile_editors[4].setEnabled(False)

    persistent_form_container = QWidget()
    persistent_form_container.setLayout(persistent_form)

    container = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(persistent_form_container)
    layout.addWidget(tile_form)
    container.setLayout(layout)
    return container, persistent_editors, tile_editors


class FE14ChapterSpawnsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.chapter_data = None
        self.dispos_model = None
        self.dispos = None
        self.terrain = None
        self.tiles_model = None
        self.terrain_mode = False
        self.initialized_selection_signal = False

        left_panel_container = QWidget()
        left_panel_layout = QVBoxLayout()
        self.toggle_editor_type_checkbox = QCheckBox()
        self.toggle_editor_type_checkbox.setText("Spawns/Terrain")
        self.toggle_editor_type_checkbox.setChecked(True)
        self.toggle_editor_type_checkbox.stateChanged.connect(self._on_mode_change_requested)
        self.toggle_coordinate_type_checkbox = QCheckBox()
        self.toggle_coordinate_type_checkbox.setText("Coordinate (1)/Coordinate (2)")
        self.toggle_coordinate_type_checkbox.setChecked(True)
        self.tree_view = QTreeView()
        left_panel_layout.addWidget(self.toggle_editor_type_checkbox)
        left_panel_layout.addWidget(self.toggle_coordinate_type_checkbox)
        left_panel_layout.addWidget(self.tree_view)
        left_panel_container.setLayout(left_panel_layout)

        self.grid = MapGrid()
        (self.dispos_form, self.dispos_editors) = _create_form(dispo.SPAWN_TEMPLATE)
        (self.terrain_form, self.terrain_persistent_editors, self.tile_editors) = _create_terrain_form()

        self.organizer = QSplitter()
        self.organizer.addWidget(left_panel_container)
        self.organizer.addWidget(self.grid)
        self.organizer.addWidget(self.dispos_form)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.organizer)
        self.setLayout(main_layout)

        self.grid.focused_spawn_changed.connect(self._on_focused_spawn_changed)

    def update_chapter_data(self, chapter_data):
        self.chapter_data = chapter_data
        self.dispos = self.chapter_data.dispos
        self.dispos_model = DisposModel(self.dispos)
        self.terrain = self.chapter_data.terrain
        self.tiles_model = TilesModel(self.terrain.tiles)
        if self.terrain_mode:
            self.tree_view.setModel(self.tiles_model)
        else:
            self.tree_view.setModel(self.dispos_model)
        self.tree_view.selectionModel().currentChanged.connect(self._on_tree_selection_changed)
        self.grid.set_chapter_data(chapter_data)
        self._update_terrain_form()

    def _update_terrain_form(self):
        for editor in self.terrain_persistent_editors:
            editor.update_target(self.terrain)

    def _on_focused_spawn_changed(self, spawn):
        for editor in self.dispos_editors:
            editor.update_target(spawn)

    def _on_mode_change_requested(self, state):
        self.organizer.widget(2).setParent(None)
        self.terrain_mode = state != QtGui.Qt.Checked
        if not self.terrain_mode:
            self.grid.transition_to_dispos_mode()
            self.organizer.addWidget(self.dispos_form)
            self.tree_view.setModel(self.dispos_model)
        else:
            self.grid.transition_to_terrain_mode()
            self.organizer.addWidget(self.terrain_form)
            self.tree_view.setModel(self.tiles_model)
        self.tree_view.selectionModel().currentChanged.connect(self._on_tree_selection_changed)

    def _on_tree_selection_changed(self, index: QModelIndex, _previous):
        data = index.data(QtCore.Qt.UserRole)
        if self.terrain_mode:
            self.grid.selected_tile = data
            for editor in self.tile_editors:
                editor.update_target(data)
