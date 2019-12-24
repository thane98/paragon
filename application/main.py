import sys

from PySide2.QtWidgets import QApplication
from services.driver import Driver
from services.settings_service import SettingsService
from ui.create_project_dialog import CreateProjectDialog
from ui.main_window import MainWindow


application = QApplication(sys.argv)
application.setStyle("fusion")
dialog = CreateProjectDialog()
main_window = None
settings_service = SettingsService()


def transition_to_main_window(project):
    global main_window
    driver = Driver(settings_service, project)
    settings_service.save_settings()
    main_window = MainWindow(transition_back_to_create_project, driver)
    main_window.show()
    print("Success!")


def transition_back_to_create_project():
    global dialog
    global main_window
    main_window = None
    settings_service.cached_project = None
    dialog = CreateProjectDialog()
    dialog.accepted.connect(on_create_project_exit)
    dialog.show()


def on_create_project_exit():
    transition_to_main_window(dialog.project)


if settings_service.cached_project:
    transition_to_main_window(settings_service.cached_project)
else:
    dialog.accepted.connect(on_create_project_exit)
    dialog.show()
sys.exit(application.exec_())
