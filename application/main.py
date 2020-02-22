import sys
import logging

from PySide2 import QtCore

from services import service_locator
from PySide2.QtWidgets import QApplication, QProgressDialog
from services.driver import Driver
from services.settings_service import SettingsService
from ui.create_project_dialog import CreateProjectDialog
from ui.error_dialog import ErrorDialog
from ui.main_window import MainWindow

logging.basicConfig(handlers=[logging.FileHandler('paragon.log', 'w', 'utf-8')], level=logging.INFO)
application = QApplication(sys.argv)
progress_dialog = QProgressDialog("Loading modules...", "Quit", 0, 0)
progress_dialog.setWindowTitle("Paragon - Loading")
progress_dialog.setAutoClose(False)
load_failed_dialog = ErrorDialog("Loading failed. See the log file for details.")
loading_thread = None
dialog = CreateProjectDialog()
main_window = None
settings_service = SettingsService()
service_locator.locator.register_static("SettingsService", settings_service)


class LoadingWorker(QtCore.QThread):
    over = QtCore.Signal()
    failed = QtCore.Signal()

    def __init__(self, project):
        QtCore.QThread.__init__(self)
        self.project = project

    def run(self):
        try:
            Driver(self.project)
            self.over.emit()
        except:
            self.failed.emit()


def show_main_window():
    driver = service_locator.locator.get_scoped("Driver")
    global main_window
    main_window = MainWindow(transition_back_to_create_project, driver)
    main_window.show()
    progress_dialog.hide()


def show_load_failed_dialog():
    load_failed_dialog.show()
    progress_dialog.hide()


def transition_to_main_window(project):
    logging.info("Transitioning to main window.")
    global loading_thread
    progress_dialog.show()
    loading_thread = LoadingWorker(project)
    loading_thread.over.connect(show_main_window)
    loading_thread.failed.connect(show_load_failed_dialog)
    loading_thread.start()


def transition_back_to_create_project():
    logging.info("Closing project and transitioning to create project.")
    global dialog
    global main_window
    main_window = None
    settings_service.cached_project = None
    service_locator.locator.clear_scoped_services()
    dialog = CreateProjectDialog()
    dialog.accepted.connect(on_create_project_exit)
    dialog.show()


def on_create_project_exit():
    transition_to_main_window(dialog.project)


if settings_service._cached_project:
    logging.info("Found cached project.")
    transition_to_main_window(settings_service._cached_project)
else:
    logging.info("Unable to find cached project.")
    dialog.accepted.connect(on_create_project_exit)
    dialog.show()
sys.exit(application.exec_())
