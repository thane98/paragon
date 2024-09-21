import logging
import traceback

from PySide6.QtWidgets import QDialogButtonBox
from paragon.model.fe14_chapter_route import FE14ChapterRoute

from paragon.ui.controllers.error_dialog import ErrorDialog

from paragon.ui import utils
from paragon.ui.views.ui_fe14_new_chapter_dialog import Ui_FE14NewChapterDialog


class FE14NewChapterDialog(Ui_FE14NewChapterDialog):
    def __init__(self, gd, chapters, model, scripts_model):
        super().__init__()
        self.model = model
        self.gd = gd
        self.chapters = chapters
        self.scripts_model = scripts_model
        self.source.setModel(model)

        self._refresh_buttons()

        self.cid.textChanged.connect(self._refresh_buttons)
        self.source.currentIndexChanged.connect(self._refresh_buttons)
        self.buttons.accepted.connect(self._on_ok)
        self.buttons.rejected.connect(self.reject)

    def _refresh_buttons(self):
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(
            bool(self.cid.text() and self.source.currentData())
        )

    def _on_ok(self):
        # Sanity check for the source CID.
        source = self.gd.key(self.source.currentData())
        if not source or not source.startswith("CID_"):
            utils.warning(
                "The template chapter has a bad CID. Corrupted chapter data?",
                "Invalid CID",
            )
            return

        # Validate the CID the user entered.
        dest = self.cid.text()
        try:
            self.chapters.validate_cid_for_new_chapter(dest)
        except ValueError as e:
            utils.warning(str(e), "Invalid CID")
            return

        # Get the route.
        if self.route.currentText() == "Birthright":
            route = FE14ChapterRoute.BIRTHRIGHT
        elif self.route.currentText() == "Conquest":
            route = FE14ChapterRoute.CONQUEST
        elif self.route.currentText() == "Revelation":
            route = FE14ChapterRoute.REVELATION
        else:
            route = FE14ChapterRoute.ALL

        # Create the new chapter.
        try:
            self.chapters.new(source, dest, scripts_model=self.scripts_model, route=route)
        except:
            logging.exception(f"Chapter creation failed source={source}, dest={dest}")
            self.error_dialog = ErrorDialog(traceback.format_exc())
            self.error_dialog.show()
            return

        utils.info(
            f"Successfully created chapter '{dest}' from template '{source}'.",
            "Success",
        )
        self.model.refresh()
        super().accept()
