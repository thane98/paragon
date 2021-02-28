import logging
import traceback

from PySide2 import QtCore
from paragon.ui.controllers.error_dialog import ErrorDialog

from paragon.ui import utils

from paragon.model.game import Game
from paragon.ui.controllers.fe13_chapter_editor_tabs import FE13ChapterEditorTabs

from paragon.ui.controllers.fe13_new_chapter_dialog import FE13NewChapterDialog
from paragon.ui.controllers.fe14_chapter_editor_tabs import FE14ChapterEditorTabs
from paragon.ui.views.ui_chapter_editor import Ui_ChapterEditor


class ChapterEditor(Ui_ChapterEditor):
    def __init__(self, ms, gs):
        super().__init__()
        self.gd = gs.data
        self.chapters = gs.chapters
        self.new_chapter_dialog = None

        # Set up the chapter list.
        rid, field_id = self.gd.table("chapters")
        models = gs.models
        self.list.setModel(models.get(rid, field_id))

        # Set up tabs.
        if gs.project.game == Game.FE13:
            self.tabs = FE13ChapterEditorTabs(ms, gs)
            self.splitter.addWidget(self.tabs)
            self.splitter.setStretchFactor(1, 1)
        elif gs.project.game == Game.FE14:
            self.tabs = FE14ChapterEditorTabs(ms, gs)
            self.splitter.addWidget(self.tabs)
            self.splitter.setStretchFactor(1, 1)

        # Set up actions.
        self.list.selectionModel().currentChanged.connect(self._on_select)
        self.new_action.triggered.connect(self._on_new)
        self.toggle_chapter_list_action.triggered.connect(self._on_toggle_chapter_list)

    def _on_new(self):
        self.new_chapter_dialog = FE13NewChapterDialog(
            self.gd, self.chapters, self.list.model()
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
