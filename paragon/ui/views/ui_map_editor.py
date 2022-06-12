from PySide2 import QtGui
from PySide2.QtGui import QKeySequence, QIcon
from PySide2.QtWidgets import (
    QWidget,
    QAction,
    QTreeView,
    QVBoxLayout,
    QShortcut,
    QSplitter,
    QStatusBar,
    QSlider,
    QLabel,
    QMenuBar,
    QMenu,
    QActionGroup,
)


class Ui_MapEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.deselect_shortcut = QShortcut(QKeySequence(QKeySequence.Cancel), self)
        self.add_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)

        self.status_bar_action = QAction("Show Status Bar")
        self.status_bar_action.setCheckable(True)
        self.status_bar_action.setChecked(True)
        self.left_panel_action = QAction("Show Left Panel")
        self.left_panel_action.setCheckable(True)
        self.left_panel_action.setChecked(True)
        self.right_panel_action = QAction("Show Right Panel")
        self.right_panel_action.setCheckable(True)
        self.right_panel_action.setChecked(True)
        self.reload_action = QAction("Reload")
        self.reload_action.setShortcut(QKeySequence("Ctrl+R"))
        self.add_faction_action = QAction("Add Faction")
        self.add_faction_action.setShortcut(QKeySequence("Ctrl+Shift+N"))
        self.add_spawn_action = QAction("Add Spawn")
        self.add_spawn_action.setShortcut(QKeySequence("Ctrl+Alt+N"))
        self.delete_action = QAction("Delete")
        self.delete_action.setShortcut(QKeySequence.Delete)
        self.add_tile_action = QAction("Add Tile")
        self.move_up_action = QAction("Move Up")
        self.move_up_action.setShortcut(QKeySequence("Ctrl+up"))
        self.move_down_action = QAction("Move Down")
        self.move_down_action.setShortcut(QKeySequence("Ctrl+down"))
        self.copy_action = QAction("Copy")
        self.copy_action.setShortcut(QKeySequence("Ctrl+C"))
        self.paste_action = QAction("Paste")
        self.paste_action.setShortcut(QKeySequence("Ctrl+V"))
        self.undo_action = QAction("Undo")
        self.undo_action.setShortcut(QKeySequence("Ctrl+Z"))
        self.redo_action = QAction("Redo")
        self.redo_action.setShortcut(QKeySequence("Ctrl+Shift+Z"))
        self.coordinate_mode_action = QAction("Use Final Spawn Positions")
        self.coordinate_mode_action.setShortcut(QKeySequence("Ctrl+T"))
        self.coordinate_mode_action.setCheckable(True)
        self.coordinate_mode_action.setChecked(True)
        self.terrain_mode_action = QAction("Terrain Mode")
        self.terrain_mode_action.setCheckable(True)
        self.rename_faction_action = QAction("Rename Faction")

        self.stamp_brush_action = QAction(QIcon("resources/icons/stamp.svg"), "Stamp")
        self.stamp_brush_action.setCheckable(True)
        self.pen_brush_action = QAction(QIcon("resources/icons/pen.svg"), "Pen (Drag)")
        self.pen_brush_action.setCheckable(True)
        self.brush_group = QActionGroup(self)
        self.brush_group.addAction(self.stamp_brush_action)
        self.brush_group.addAction(self.pen_brush_action)
        self.pen_brush_action.setChecked(True)

        view_menu = QMenu("View")
        view_menu.addActions(
            [self.status_bar_action, self.left_panel_action, self.right_panel_action]
        )
        view_menu.addSeparator()
        view_menu.addActions([self.reload_action])

        edit_menu = QMenu("Edit")
        edit_menu.addActions([self.undo_action, self.redo_action])
        edit_menu.addSeparator()
        edit_menu.addActions([self.copy_action, self.paste_action])

        dispos_menu = QMenu("Spawns")
        dispos_menu.addAction(self.coordinate_mode_action)
        dispos_menu.addSeparator()
        dispos_menu.addActions([self.move_up_action, self.move_down_action])
        dispos_menu.addSeparator()
        dispos_menu.addActions(
            [self.add_faction_action, self.add_spawn_action, self.add_tile_action]
        )
        dispos_menu.addSeparator()
        dispos_menu.addAction(self.rename_faction_action)
        dispos_menu.addSeparator()
        dispos_menu.addActions([self.delete_action])

        brush_menu = QMenu("Brush")
        brush_menu.addActions([self.stamp_brush_action, self.pen_brush_action])

        terrain_menu = QMenu("Terrain")
        terrain_menu.addAction(self.terrain_mode_action)
        terrain_menu.addSeparator()
        terrain_menu.addActions([self.add_tile_action])
        terrain_menu.addSeparator()
        terrain_menu.addMenu(brush_menu)

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
        self.zoom_slider.setRange(0, 5)
        self.zoom_slider.setValue(1)
        self.zoom_slider.setMaximumWidth(200)
        self.zoom_slider.setOrientation(QtGui.Qt.Horizontal)

        self.tile_label = QLabel("Tile: None")
        self.spawn_label = QLabel("Spawn: None")
        self.x_label = QLabel("X: 0")
        self.y_label = QLabel("Y: 0")
        spacer = QLabel()
        spacer.setFixedWidth(15)

        self.status_bar = QStatusBar()
        self.status_bar.addPermanentWidget(self.x_label)
        self.status_bar.addPermanentWidget(spacer)
        self.status_bar.addPermanentWidget(self.y_label)
        self.status_bar.addPermanentWidget(spacer)
        self.status_bar.addPermanentWidget(self.spawn_label)
        self.status_bar.addPermanentWidget(spacer)
        self.status_bar.addPermanentWidget(self.tile_label)
        self.status_bar.addPermanentWidget(self.zoom_slider)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(menu_bar)
        self.main_layout.addWidget(self.splitter)
        self.main_layout.addWidget(self.status_bar)
        self.main_layout.setStretch(1, 1)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)
