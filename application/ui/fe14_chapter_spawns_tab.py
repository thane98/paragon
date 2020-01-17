from PySide2 import QtWidgets
from PySide2.QtWidgets import QWidget, QTreeView, QSplitter, QVBoxLayout, QFormLayout, QScrollArea

from model.fe14 import dispo
from model.fe14.dispo_model import DisposModel
from ui.map_grid import MapGrid


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
        self.initialized_selection_signal = False

        self.spawn_tree_view = QTreeView()
        self.grid = MapGrid()
        (self.form, self.editors) = _create_form()

        organizer = QSplitter()
        organizer.addWidget(self.spawn_tree_view)
        organizer.addWidget(self.grid)
        organizer.addWidget(self.form)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(organizer)
        self.setLayout(main_layout)

    def update_chapter_data(self, chapter_data):
        self.chapter_data = chapter_data
        self.dispos = self.chapter_data.dispos
        self.model = DisposModel(self.dispos)
        self.spawn_tree_view.setModel(self.model)
        self.grid.set_chapter_data(chapter_data)
