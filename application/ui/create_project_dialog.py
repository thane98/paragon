import logging

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QDialog, QFileDialog, QErrorMessage
from ui.autogen.ui_create_project_dialog import Ui_CreateProject
from model.project import Project


class CreateProjectDialog(QDialog, Ui_CreateProject):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.project = None
        self.message_dialog = QErrorMessage()
        self.buttonBox.buttons()[0].setEnabled(False)
        self.setWindowTitle("Create Project")
        self.setWindowIcon(QIcon("paragon.ico"))

        self.rom_button.clicked.connect(lambda: self._open_file_and_set_field("rom_field"))
        self.project_path_button.clicked.connect(lambda: self._open_file_and_set_field("project_path_field"))
        self.rom_field.textChanged.connect(self._update_ok_button_enabled)
        self.project_path_field.textChanged.connect(self._update_ok_button_enabled)

    def show(self):
        super().show()
        self.project = None

    def _update_ok_button_enabled(self):
        if self.rom_field.text() and self.project_path_field.text():
            self.buttonBox.buttons()[0].setEnabled(True)
        else:
            self.buttonBox.buttons()[0].setEnabled(False)

    def _open_file_and_set_field(self, attr):
        dir_name = QFileDialog.getExistingDirectory(self)
        if dir_name:
            field = getattr(self, attr)
            field.setText(dir_name)

    def accept(self):
        rom_path = self.rom_field.text()
        project_path = self.project_path_field.text()
        game = self.game_box.currentIndex()
        language = self.language_box.currentIndex()

        try:
            self.project = Project(rom_path, project_path, game, language)
        except NotADirectoryError:
            logging.exception("Error during project creation.")
            self.message_dialog.showMessage("One of the specified paths is not a directory.", "error")
        except IndexError:
            logging.exception("Error during project creation.")
            self.message_dialog.showMessage("Invalid game or language.", "error")
        except NotImplementedError:
            logging.exception("Error during project creation.")
            self.message_dialog.showMessage("Attempted to create a project for an unsupported game.")
        except:
            logging.exception("Unknown error during project creation.")
            self.message_dialog.showMessage("An unknown error occurred during project creation.")

        if self.project:
            super().accept()
