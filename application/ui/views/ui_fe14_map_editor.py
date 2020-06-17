from PySide2 import QtCore
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QMainWindow, QToolBar, QAction, QTreeView, QListView, QScrollArea, \
    QSplitter, QStatusBar, QLabel, QMenu, QShortcut

from ui.fe14.fe14_spawn_editor_pane import FE14SpawnEditorPane
from ui.fe14.fe14_terrain_editor_pane import FE14TerrainEditorPane
from ui.widgets.fe14_map_grid import FE14MapGrid


class Ui_FE14MapEditor(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.toolbar = QToolBar()
        self.toggle_coordinate_type_action = QAction("Toggle Coordinate Type")
        self.refresh_action = QAction("Refresh")
        self.refresh_action.setShortcut(QKeySequence("Ctrl+R"))
        self.copy_spawn_action = QAction("Copy Spawn")
        self.copy_spawn_action.setShortcut(QKeySequence("Ctrl+C"))
        self.paste_spawn_action = QAction("Paste Spawn")
        self.paste_spawn_action.setShortcut(QKeySequence("Ctrl+V"))
        self.add_spawn_action = QAction("Add Spawn")
        self.delete_spawn_action = QAction("Delete Spawn")
        self.add_group_action = QAction("Add Group")
        self.delete_group_action = QAction("Delete Group")
        self.add_tile_action = QAction("Add Tile")
        self.toggle_mode_action = QAction("Toggle Mode")
        self.undo_action = QAction("Undo")
        self.undo_action.setShortcut(QKeySequence("Ctrl+Z"))
        self.redo_action = QAction("Redo")
        self.redo_action.setShortcut(QKeySequence("Ctrl+Shift+Z"))
        self.toolbar.addActions([self.toggle_coordinate_type_action, self.refresh_action])
        self.toolbar.addSeparator()
        self.toolbar.addActions([
            self.copy_spawn_action,
            self.paste_spawn_action,
            self.add_spawn_action,
            self.delete_spawn_action,
            self.add_group_action,
            self.delete_group_action
        ])
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.add_tile_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.toggle_mode_action)
        self.toolbar.addSeparator()
        self.toolbar.addActions([self.undo_action, self.redo_action])
        self.addToolBar(self.toolbar)

        self.model_view = QTreeView()
        self.model_view.setHeaderHidden(True)
        self.grid = FE14MapGrid()
        self.grid_scroll = QScrollArea()
        self.grid_scroll.setWidgetResizable(True)
        self.grid_scroll.setWidget(self.grid)
        self.tile_list = QListView()
        self.terrain_pane = FE14TerrainEditorPane()
        self.spawn_pane = FE14SpawnEditorPane()

        self.model_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.model_view_context_menu = QMenu()
        self.model_view_context_menu.addActions([self.toggle_coordinate_type_action, self.refresh_action])
        self.model_view_context_menu.addSeparator()
        self.model_view_context_menu.addActions([
            self.copy_spawn_action,
            self.paste_spawn_action,
            self.add_spawn_action,
            self.delete_spawn_action,
            self.add_group_action,
            self.delete_group_action
        ])
        self.model_view_context_menu.addSeparator()
        self.model_view_context_menu.addAction(self.add_tile_action)
        self.model_view_context_menu.addSeparator()
        self.model_view_context_menu.addAction(self.toggle_mode_action)
        self.model_view_context_menu.addSeparator()
        self.model_view_context_menu.addActions([self.undo_action, self.redo_action])

        self.status_bar = QStatusBar()
        self.coordinate_type_label = QLabel()
        self.status_bar.addPermanentWidget(self.coordinate_type_label)
        self.setStatusBar(self.status_bar)

        self.main_widget = QSplitter()
        self.main_widget.setOrientation(QtCore.Qt.Horizontal)
        self.main_widget.addWidget(self.model_view)
        self.main_widget.addWidget(self.grid_scroll)
        self.main_widget.addWidget(self.spawn_pane)
        self.main_widget.addWidget(self.terrain_pane)
        self.setCentralWidget(self.main_widget)
