import logging
from typing import cast

from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMainWindow, QFileDialog, QStyleFactory, QActionGroup, QAction, QMessageBox

from model.qt.module_filter_model import ModuleFilterModel
from model.qt.open_files_model import OpenFilesModel
from module.module import Module
from module.table_module import TableModule
from services.service_locator import locator
from ui.autogen.ui_main_window import Ui_MainWindow
from ui.error_dialog import ErrorDialog
from ui.export_dialog import ExportDialog
from ui.object_editor import ObjectEditor
from ui.simple_editor import SimpleEditor


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.open_editors = {}
        self.proxy_model = None
        self.open_file_model = None
        self.error_dialog = None
        self.export_dialog = None
        self.theme_action_group = QActionGroup(self)
        self.theme_menu = None
        self.theme_info_dialog = self._create_theme_info_dialog()
        self.setWindowTitle("Paragon")
        self.setWindowIcon(QIcon("paragon.ico"))
        self._set_view_models()
        self._install_signal_handlers()
        self._populate_themes_menu()

        logging.info("Opened main window.")

    def _on_export_triggered(self):
        self.export_dialog = ExportDialog()
        self.export_dialog.show()

    def _on_import_triggered(self):
        file_name, ok = QFileDialog.getOpenFileName(self, "Select file.", filter="*.json")
        if ok:
            try:
                locator.get_scoped("Driver").import_from_json(file_name)
                self.statusbar.showMessage("Import succeeded!", 5000)
            except:
                logging.exception("An error occurred during importing.")
                self.error_dialog = ErrorDialog("Importing failed. See the log for details.")
                self.error_dialog.show()
                self.statusbar.showMessage("Importing failed.", 5000)

    @staticmethod
    def _create_theme_info_dialog():
        theme_info_dialog = QMessageBox()
        theme_info_dialog.setText("This theme will be used the next time you run Paragon.")
        theme_info_dialog.setWindowTitle("Paragon")
        theme_info_dialog.setWindowIcon(QIcon("paragon.ico"))
        return theme_info_dialog

    def closeEvent(self, event: QtGui.QCloseEvent):
        locator.get_static("SettingsService").save_settings()
        event.accept()

    def _populate_themes_menu(self):
        self.theme_menu = self.menuOptions.addMenu("Theme")
        current_theme = locator.get_static("SettingsService").get_theme()
        for theme in QStyleFactory.keys():
            action = self.theme_menu.addAction(theme)
            action.setCheckable(True)
            if theme == current_theme:
                action.setChecked(True)
            action.setActionGroup(self.theme_action_group)
            action.changed.connect(lambda a=action, t=theme: self._on_theme_changed(a, t))

    def _set_view_models(self):
        module_service = locator.get_scoped("ModuleService")
        dedicated_editors_service = locator.get_scoped("DedicatedEditorsService")
        self.proxy_model = ModuleFilterModel()
        self.open_file_model = OpenFilesModel()

        self.proxy_model.setSourceModel(module_service.get_module_model())
        self.module_list_view.setModel(self.proxy_model)
        self.editors_list_view.setModel(dedicated_editors_service.get_dedicated_editors_model())
        self.file_list_view.setModel(self.open_file_model)
        self.module_list_view.setHeaderHidden(True)
        self.module_list_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    def _install_signal_handlers(self):
        self.search_field.textChanged.connect(self._update_filter)
        self.module_list_view.activated.connect(self._on_module_activated)
        self.editors_list_view.activated.connect(self._on_editor_activated)
        self.file_list_view.selectionModel().currentRowChanged.connect(self._on_file_list_selection_change)
        self.close_button.clicked.connect(self._on_close_file_pressed)
        self.action_save.triggered.connect(self.save)
        self.action_reload.triggered.connect(self.reload_project)
        self.action_close.triggered.connect(self.close)
        self.action_quit.triggered.connect(self.quit_application)
        self.action_export.triggered.connect(self._on_export_triggered)
        self.action_import.triggered.connect(self._on_import_triggered)

    def _update_filter(self, new_filter):
        self.proxy_model.setFilterRegExp(new_filter.lower())

    def save(self):
        driver = locator.get_scoped("Driver")
        if driver.save():
            self.statusbar.showMessage("Save succeeded!", 5000)
        else:
            self.statusbar.showMessage("Save failed. See the log for details.", 5000)

    def close(self):
        self.proxy_model.setSourceModel(None)
        self.hide()
        state_machine = locator.get_static("StateMachine")
        state_machine.transition("SelectProject")

    def reload_project(self):
        logging.info("Reload project triggered.")
        self.proxy_model.setSourceModel(None)
        self.hide()
        state_machine = locator.get_static("StateMachine")
        state_machine.transition("Loading")

    @staticmethod
    def quit_application():
        exit(0)

    def _on_file_list_selection_change(self, index):
        self.close_button.setEnabled(self.open_file_model.can_close(index.row()))

    def _on_close_file_pressed(self):
        self.open_file_model.close(self.file_list_view.currentIndex().row())

    def _on_module_activated(self, index):
        logging.info("Module " + str(index.row()) + " activated.")
        module_model = locator.get_scoped("ModuleService").get_module_model()
        index = self.proxy_model.mapToSource(index)
        item = module_model.itemFromIndex(index)
        if item.data():
            module = item.data()
            try:
                self._open_module_editor(module)
            except:
                logging.exception("Failed to open editor for module %s" % module.name)
                self.error_dialog = ErrorDialog("Unable to open module %s. See the log for details." % module.name)
                self.error_dialog.show()

    def _open_module_editor(self, module: Module):
        if module in self.open_editors:
            logging.info(module.name + " is cached. Reopening editor...")
            editor = self.open_editors[module]
        elif not module.unique:
            module = self._handle_common_module_open(module)
            if not module:
                return
            editor = self._get_editor_for_module(module)
        else:
            editor = self._get_editor_for_module(module)

        module_service = locator.get_scoped("ModuleService")
        module_service.set_module_in_use(module)
        self.open_editors[module] = editor
        editor.show()

    def _on_theme_changed(self, action: QAction, new_theme: str):
        if action.isChecked():
            locator.get_static("SettingsService").set_theme(new_theme)
            self.theme_info_dialog.exec_()

    def _get_editor_for_module(self, module):
        if module.type == "table":
            logging.info("Opening " + module.name + " as a TableModule.")
            editor = SimpleEditor(cast(TableModule, module))
        elif module.type == "object":
            logging.info("Opening " + module.name + " as an ObjectModule.")
            editor = ObjectEditor(module)
        else:
            logging.error("Attempted to open an unsupported module type.")
            raise NotImplementedError
        return editor

    def _handle_common_module_open(self, module):
        logging.info(module.name + " is a common module. Prompting for a file...")
        target_file = QFileDialog.getOpenFileName(self)
        if not target_file[0]:
            logging.info("No file selected - operation aborted.")
            return
        logging.info("File selected. Opening common module...")

        common_module_service = locator.get_scoped("CommonModuleService")
        module = common_module_service.open_common_module(module, target_file[0])

        # Hack to keep the display for the open file model consistent.
        self.open_file_model.beginResetModel()
        self.open_file_model.endResetModel()
        return module

    @staticmethod
    def _on_editor_activated(index):
        dedicated_editors_service = locator.get_scoped("DedicatedEditorsService")
        model = dedicated_editors_service.get_dedicated_editors_model()
        service = model.data(index, QtCore.Qt.UserRole)
        editor = service.get_editor()
        if editor:
            editor.show()
