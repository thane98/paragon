import logging
import sys

from core.state_machine import State
from services.service_locator import locator
from ui.create_project_dialog import CreateProjectDialog


class CreateProjectState(State):
    def __init__(self):
        super().__init__("CreateProject")
        self.project = None
        self.dialog = None

    def act(self):
        logging.info("Entered CreateProject state.")
        self.dialog = CreateProjectDialog()
        self.dialog.accepted.connect(self._on_dialog_accepted)
        self.dialog.rejected.connect(self._on_dialog_rejected)
        self.dialog.exec_()

    def _on_dialog_accepted(self):
        self.project = self.dialog.project
        locator.get_static("StateMachine").transition("Loading")

    @staticmethod
    def _on_dialog_rejected():
        sys.exit(0)
