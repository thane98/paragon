import sys
import logging

from services import service_locator
from PySide2.QtWidgets import QApplication
from services.driver import Driver
from services.settings_service import SettingsService
from ui.create_project_dialog import CreateProjectDialog
from ui.main_window import MainWindow

logging.basicConfig(handlers=[logging.FileHandler('paragon.log', 'w', 'utf-8')], level=logging.INFO)
application = QApplication(sys.argv)
dialog = CreateProjectDialog()
main_window = None
settings_service = SettingsService()
service_locator.locator.register_static("SettingsService", settings_service)


def transition_to_main_window(project):
    logging.info("Transitioning to main window.")

    global main_window
    driver = Driver(project)
    settings_service.save_settings()
    main_window = MainWindow(transition_back_to_create_project, driver)
    main_window.show()


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


if settings_service.cached_project:
    logging.info("Found cached project.")
    transition_to_main_window(settings_service.cached_project)
else:
    logging.info("Unable to find cached project.")
    dialog.accepted.connect(on_create_project_exit)
    dialog.show()
sys.exit(application.exec_())
