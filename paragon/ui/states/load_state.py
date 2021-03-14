import logging

from PySide2.QtCore import QObject, QThreadPool
from paragon.core.workers.load_project_worker import LoadProjectWorker
from paragon.ui.controllers.error_dialog import ErrorDialog

from paragon.ui.controllers.project_loading_dialog import ProjectLoadingDialog


class LoadState(QObject):
    def __init__(self):
        QObject.__init__(self)
        self.dialog = None
        self.worker = None
        self.ms = None
        self.canceled = False

    def run(self, **kwargs):
        self.canceled = False
        self.ms = kwargs["main_state"]
        project = kwargs["project"]

        self.worker = LoadProjectWorker(self.ms.config, project)
        self.worker.succeeded.connect(self._on_load_succeeded)
        self.worker.error.connect(self._on_load_error)

        self.dialog = ProjectLoadingDialog(project)
        self.dialog.canceled.connect(self._on_load_canceled)
        self.dialog.show()

        # TODO: Make this multithreaded again.
        self.worker.run()

    def _on_load_succeeded(self, game_state):
        if self.canceled:
            return
        if self.dialog:
            self.dialog.reset()
        self.ms.sm.transition("UIMain", main_state=self.ms, game_state=game_state)

    def _on_load_error(self, error_info):
        if self.canceled:
            return
        if self.dialog:
            self.dialog.reset()
        self.dialog = ErrorDialog(error_info[0])
        self.dialog.finished.connect(self._on_error_dialog_finished)
        self.dialog.show()

    def _on_load_canceled(self):
        self.canceled = True
        try:
            QThreadPool.globalInstance().cancel(self.worker)
        except:
            logging.exception("Failed to cancel load project worker.")
        self.ms.sm.transition("SelectProject", main_state=self.ms)

    def _on_error_dialog_finished(self):
        self.ms.sm.transition("SelectProject", main_state=self.ms)

    def on_exit(self):
        if self.dialog and self.dialog is ProjectLoadingDialog:
            self.dialog.reset()
        self.dialog = None
        self.worker = None
        self.ms = None
        self.canceled = None

    def get_name(self) -> str:
        return "Load"
