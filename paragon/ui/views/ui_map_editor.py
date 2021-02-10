from PySide2 import QtGui
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import (
    QWidget,
    QAction,
    QTreeView,
    QVBoxLayout,
    QShortcut,
    QSplitter,
    QStatusBar,
    QSlider,
    QLabel, QMenuBar, QMenu, )


class Ui_MapEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.deselect_shortcut = QShortcut(QKeySequence(QKeySequence.Cancel), self)
        self.delete_shortcut = QShortcut(QKeySequence(QKeySequence.Delete), self)
        self.add_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        self.undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        self.redo_shortcut = QShortcut(QKeySequence("Ctrl+Shift+Z"), self)
        self.copy_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        self.paste_shortcut = QShortcut(QKeySequence("Ctrl+V"), self)

        self.status_bar_action = QAction("Show Status Bar")
        self.status_bar_action.setCheckable(True)
        self.status_bar_action.setChecked(True)
        self.left_panel_action = QAction("Show Left Panel")
        self.left_panel_action.setCheckable(True)
        self.left_panel_action.setChecked(True)
        self.right_panel_action = QAction("Show Right Panel")
        self.right_panel_action.setCheckable(True)
        self.right_panel_action.setChecked(True)
        self.add_faction_action = QAction("Add Faction")
        self.add_spawn_action = QAction("Add Spawn")
        self.delete_action = QAction("Delete")
        self.add_tile_action = QAction("Add Tile")
        self.move_up_action = QAction("Move Up")
        self.move_down_action = QAction("Move Down")
        self.copy_action = QAction("Copy")
        self.paste_action = QAction("Paste")
        self.undo_action = QAction("Undo")
        self.redo_action = QAction("Redo")
        self.coordinate_mode_action = QAction("Use Final Spawn Positions")
        self.coordinate_mode_action.setCheckable(True)
        self.coordinate_mode_action.setChecked(True)
        self.terrain_mode_action = QAction("Terrain Mode")
        self.terrain_mode_action.setCheckable(True)

        view_menu = QMenu("View")
        view_menu.addActions([self.status_bar_action, self.left_panel_action, self.right_panel_action])

        edit_menu = QMenu("Edit")
        edit_menu.addActions([self.undo_action, self.redo_action])
        edit_menu.addSeparator()
        edit_menu.addActions([self.copy_action, self.paste_action])

        dispos_menu = QMenu("Spawns")
        dispos_menu.addAction(self.coordinate_mode_action)
        dispos_menu.addSeparator()
        dispos_menu.addActions([self.move_up_action, self.move_down_action])
        dispos_menu.addSeparator()
        dispos_menu.addActions([self.add_faction_action, self.add_spawn_action, self.add_tile_action])
        dispos_menu.addSeparator()
        dispos_menu.addActions([self.delete_action])

        terrain_menu = QMenu("Terrain")
        terrain_menu.addAction(self.terrain_mode_action)
        terrain_menu.addSeparator()
        terrain_menu.addActions([self.add_tile_action])

        menu_bar = QMenuBar()
        menu_bar.addMenu(view_menu)
        menu_bar.addMenu(edit_menu)
        menu_bar.addMenu(dispos_menu)
        menu_bar.addMenu(terrain_menu)

        self.tree = QTreeView()
        self.tree.setHeaderHidden(True)

        self.splitter = QSplitter()
        self.splitter.addWidget(self.tree)

        self.zoom_slider = QSlider()
        self.zoom_slider.setRange(1, 5)
        self.zoom_slider.setMaximumWidth(200)
        self.zoom_slider.setOrientation(QtGui.Qt.Horizontal)

        self.tile_label = QLabel("Tile: None")
        self.spawn_label = QLabel("Spawn: None")
        spacer = QLabel()
        spacer.setFixedWidth(15)

        self.status_bar = QStatusBar()
        self.status_bar.addPermanentWidget(self.tile_label)
        self.status_bar.addPermanentWidget(spacer)
        self.status_bar.addPermanentWidget(self.spawn_label)
        self.status_bar.addPermanentWidget(self.zoom_slider)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(menu_bar)
        self.main_layout.addWidget(self.splitter)
        self.main_layout.addWidget(self.status_bar)
        self.main_layout.setStretch(1, 1)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)
