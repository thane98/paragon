from PySide2 import QtGui, QtWidgets
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QWidget, QTreeView, QSplitter, QVBoxLayout, QGridLayout, QLabel, QFormLayout, QScrollArea

from model.fe14 import dispo
from model.fe14.dispo_model import DisposModel


def _create_spawn_grid():
    grid_widget = QWidget()
    grid_widget.setContentsMargins(0, 0, 0, 0)
    layout = QGridLayout()
    grid = []
    for r in range(0, 32):
        row = []
        for c in range(0, 32):
            label = QLabel()
            label.setAlignment(QtGui.Qt.AlignCenter)
            label.setStyleSheet("border: 1px dashed black")
            layout.addWidget(label, r, c)
            row.append(label)
        grid.append(row)
    layout.setVerticalSpacing(0)
    layout.setHorizontalSpacing(0)
    grid_widget.setLayout(layout)
    return grid, grid_widget


def _create_form():
    template = dispo.SPAWN_TEMPLATE
    editors = []
    layout = QFormLayout()
    for (key, prop) in template.items():
        label = QtWidgets.QLabel(key)
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


class FE14ChapterSpawnsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.chapter_data = None
        self.model = None
        self.dispos = None

        self.spawn_tree_view = QTreeView()
        (self.form, self.editors) = _create_form()

        organizer = QSplitter()
        (self.grid, grid_widget) = _create_spawn_grid()
        organizer.addWidget(self.spawn_tree_view)
        organizer.addWidget(grid_widget)
        organizer.addWidget(self.form)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(organizer)
        self.setLayout(main_layout)

    def update_chapter_data(self, chapter_data):
        self.chapter_data = chapter_data
        self.dispos = self.chapter_data.dispos
        self.model = DisposModel(self.dispos)
        self.spawn_tree_view.setModel(self.model)

        self._clear_grid()
        for faction in self.dispos.factions:
            for spawn in faction.spawns:
                coordinate = spawn["Coordinate (1)"].value
                team = spawn["Team"].value
                target_label = self.grid[coordinate[1]][coordinate[0]]
                if team == 0:
                    pixmap = QPixmap("player.png")
                elif team == 1:
                    pixmap = QPixmap("enemy.png")
                else:
                    pixmap = QPixmap("allied.png")
                target_label.setPixmap(pixmap)

    def _clear_grid(self):
        for r in range(0, 32):
            for c in range(0, 32):
                self.grid[r][c].setPixmap(None)
