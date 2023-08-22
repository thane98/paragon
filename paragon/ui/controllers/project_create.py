from typing import Optional

from PySide2.QtCore import Signal
from PySide2.QtWidgets import QDialogButtonBox, QMessageBox

from paragon.core import sanity_check
from paragon.model.project import Project
from paragon.model.game import Game
from paragon.model.language import Language
from paragon.ui.views.ui_project_create import Ui_ProjectCreate


class ProjectCreate(Ui_ProjectCreate):
    project_saved = Signal(Project)

    def __init__(self, project: Optional[Project] = None, parent=None):
        super().__init__(parent)

        self.project_name_line_edit.setText(project.name if project else None)
        self.rom_selector.set_text(project.rom_path if project else None)
        self.output_directory_selector.set_text(
            project.output_path if project else None
        )
        if project:
            for i, g in enumerate(Game):
                if project.game == g:
                    self.project_game_combo_box.setCurrentIndex(i)
                    break
            for i, l in enumerate(Language):
                if project.language == l:
                    self.project_language_combo_box.setCurrentIndex(i)
                    break

        self.project_name_line_edit.textChanged.connect(self._update_buttons)
        self.rom_selector.selection_changed.connect(self._update_buttons)
        self.output_directory_selector.selection_changed.connect(self._update_buttons)
        self.project_game_combo_box.currentIndexChanged.connect(self._update_buttons)
        self.project_language_combo_box.currentIndexChanged.connect(
            self._update_buttons
        )
        self.actions_button_box.accepted.connect(self._on_accepted)
        self.actions_button_box.rejected.connect(self._on_rejected)

        self._update_buttons()

    def _on_accepted(self):
        project = Project(
            name=self.project_name_line_edit.text(),
            rom_path=self.rom_selector.text,
            output_path=self.output_directory_selector.text,
            game=self.project_game_combo_box.value(),
            language=self.project_language_combo_box.value(),
        )
        if not sanity_check.sanity_check_files(project):
            if sanity_check.sanity_check_romfs_bin(project):
                message = "Your extracted RomFS is missing critical files. Create project anyway?"
            else:
                message = "It looks like you selected a directory with a romfs.bin, *not* an extracted RomFS. Create project anyway?"
            if not QMessageBox.question(self, "Sanity Check Failed", message):
                return
        self.project_saved.emit(project)
        self.close()

    def _on_rejected(self):
        self.close()

    def _update_buttons(self):
        self.actions_button_box.button(QDialogButtonBox.Save).setEnabled(
            self._selections_are_valid()
        )

    def _selections_are_valid(self):
        return bool(
            self.project_name_line_edit.text()
            and self.rom_selector.text
            and self.output_directory_selector.text
            and self.project_game_combo_box.value()
            and self.project_language_combo_box.value()
        )
