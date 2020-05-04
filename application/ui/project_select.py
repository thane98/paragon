from PySide2 import QtGui
from PySide2.QtCore import QModelIndex
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMainWindow, QTableView, QHeaderView, QAbstractItemView

from model.qt.project_model import ProjectModel
from services.service_locator import locator
from ui.autogen.ui_project_select import Ui_project_select
from ui.create_project_dialog import CreateProjectDialog


class ProjectSelectWindow(QMainWindow, Ui_project_select):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Project Select")
        self.setWindowIcon(QIcon("paragon.ico"))
        self.create_project_dialog = None
        self.current_project = None

        settings_service = locator.get_static("SettingsService")
        self.model: ProjectModel = settings_service.get_project_model()
        self.table_view.setModel(self.model)
        self.table_view.verticalHeader().hide()
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.remember_check_box.setChecked(settings_service.should_remember_last_project())

        self.action_create.triggered.connect(self._on_create_project_clicked)
        self.action_remove.triggered.connect(self._on_remove_clicked)
        self.action_move_up.triggered.connect(self._on_move_up_clicked)
        self.action_move_down.triggered.connect(self._on_move_down_clicked)
        self.remember_check_box.stateChanged.connect(self._on_remember_project_checked)
        self.table_view.activated.connect(self._on_project_activated)
        self.table_view.selectionModel().currentRowChanged.connect(self._on_selected_row_changed)

    def closeEvent(self, event: QtGui.QCloseEvent):
        locator.get_static("SettingsService").save_settings()
        if self.create_project_dialog:
            self.create_project_dialog.hide()
        event.accept()

    def _on_create_project_clicked(self):
        if self.create_project_dialog:
            self.create_project_dialog.hide()
        self.create_project_dialog = CreateProjectDialog()
        self.create_project_dialog.accepted.connect(self._on_create_project_accepted)
        self.create_project_dialog.show()

    def _on_create_project_accepted(self):
        if self.create_project_dialog:
            self.current_project = self.create_project_dialog.project
            self.model.add_project(self.current_project)
            self.hide()
            locator.get_static("StateMachine").transition("Loading")

    def _on_remove_clicked(self):
        index = self.table_view.currentIndex()
        if index.isValid():
            self.model.remove_project(index)

    def _on_move_up_clicked(self):
        index = self.table_view.currentIndex()
        if index.isValid():
            new_row = self.model.move_project_up(index)
            self.table_view.selectRow(new_row)

    def _on_move_down_clicked(self):
        index = self.table_view.currentIndex()
        if index.isValid():
            new_row = self.model.move_project_down(index)
            self.table_view.selectRow(new_row)

    def _on_project_activated(self, index: QModelIndex):
        true_index = self.model.index(index.row(), 0)
        item = self.model.itemFromIndex(true_index)
        self.current_project = item.data()
        self.hide()
        locator.get_static("StateMachine").transition("Loading")

    def _on_selected_row_changed(self, index: QModelIndex):
        self.action_remove.setEnabled(index.isValid())
        self.action_move_up.setEnabled(index.isValid())
        self.action_move_down.setEnabled(index.isValid())

    @staticmethod
    def _on_remember_project_checked(new_state: int):
        locator.get_static("SettingsService").set_remember_last_project(new_state != 0)
