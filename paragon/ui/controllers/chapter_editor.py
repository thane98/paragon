import logging
import traceback

from PySide2 import QtCore
from PySide2.QtCore import QSortFilterProxyModel

from paragon.ui.controllers.error_dialog import ErrorDialog

from paragon.ui import utils

from paragon.model.game import Game
from paragon.ui.controllers.fe13_chapter_editor_tabs import FE13ChapterEditorTabs

from paragon.ui.controllers.new_chapter_dialog import NewChapterDialog
from paragon.ui.controllers.fe14_chapter_editor_tabs import FE14ChapterEditorTabs
from paragon.ui.controllers.fe14_new_chapter_dialog import FE14NewChapterDialog
from paragon.ui.controllers.fe15_chapter_editor_tabs import FE15ChapterEditorTabs
from paragon.ui.views.ui_chapter_editor import Ui_ChapterEditor


class ChapterEditor(Ui_ChapterEditor):
    def __init__(self, ms, gs):
        super().__init__()
        self.project = gs.project
        self.models = gs.models
        self.gd = gs.data
        self.chapters = gs.chapters
        self.new_chapter_dialog = None

        # Set up the chapter list.
        rid, field_id = self.gd.table("chapters")
        models = gs.models
        self.model = models.get(rid, field_id)
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.proxy_model.setSourceModel(self.model)
        self.list.setModel(self.proxy_model)

        # Set up tabs.
        if gs.project.game == Game.FE13:
            self.tabs = FE13ChapterEditorTabs(ms, gs)
            self.splitter.addWidget(self.tabs)
            self.splitter.setStretchFactor(1, 1)
        elif gs.project.game == Game.FE14:
            self.tabs = FE14ChapterEditorTabs(ms, gs)
            self.splitter.addWidget(self.tabs)
            self.splitter.setStretchFactor(1, 1)
        elif gs.project.game == Game.FE15:
            self.tabs = FE15ChapterEditorTabs(ms, gs)
            self.splitter.addWidget(self.tabs)
            self.splitter.setStretchFactor(1, 1)

        # Set up actions.
        self.list.selectionModel().currentChanged.connect(
            self._on_select, QtCore.Qt.UniqueConnection
        )
        self.new_action.triggered.connect(self._on_new, QtCore.Qt.UniqueConnection)
        self.toggle_chapter_list_action.triggered.connect(
            self._on_toggle_chapter_list, QtCore.Qt.UniqueConnection
        )
        self.search.textChanged.connect(self._on_search, QtCore.Qt.UniqueConnection)

    def _on_search(self):
        self.proxy_model.setFilterRegExp(self.search.text())

    def _on_new(self):
        rid, field_id = self.gd.table("chapters")
        chapter_model = self.models.get(rid, field_id)
        if self.project.game == Game.FE13 or self.project.game == Game.FE15:
            self.new_chapter_dialog = NewChapterDialog(
                self.gd, self.chapters, chapter_model
            )
        elif self.project.game == Game.FE14:
            self.new_chapter_dialog = FE14NewChapterDialog(
                self.gd, self.chapters, chapter_model
            )
        self.new_chapter_dialog.show()

    def _on_toggle_chapter_list(self):
        self.left_widget.setVisible(not self.left_widget.isVisible())

    def _on_select(self):
        index = self.list.currentIndex()
        if not index:
            self.tabs.set_target(None)
            return
        decl = self.list.model().data(index, QtCore.Qt.UserRole)
        if not decl:
            self.tabs.set_target(None)
            return
        key = self.gd.key(decl)
        if not key:
            utils.warning(
                "The chapter has a bad CID. Corrupted chapter data?", "Invalid CID"
            )
            self.list.clearSelection()
            return
        try:
            data = self.chapters.load(key)
            self.chapters.set_dirty(data, True)
            self.tabs.set_target(data)
        except:
            logging.exception(f"Failed to load chapter {key}")
            self.error_dialog = ErrorDialog(traceback.format_exc())
            self.error_dialog.show()
