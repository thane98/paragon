from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QHeaderView

from paragon.core import sanity_check
from paragon.model.project_model import ProjectModel
from paragon.ui.controllers.project_create import ProjectCreate
from paragon.ui.views.ui_project_select import Ui_ProjectSelect


class ProjectSelect(Ui_ProjectSelect):
    def __init__(self, main_state):
        super().__init__()
        self.ms = main_state
        self.model = ProjectModel(main_state.config.projects)
        self.thread_pool = QThreadPool()
        self.worker = None
        self.dialog = None

        self.table.setModel(self.model)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)

        self.remember_check.setChecked(self.ms.config.remember_project)

        self.new_action.triggered.connect(self._on_new)
        self.edit_action.triggered.connect(self._on_edit)
        self.delete_action.triggered.connect(self._on_delete)
        self.open_action.triggered.connect(self._on_open)
        self.move_up_action.triggered.connect(self._on_move_up)
        self.move_down_action.triggered.connect(self._on_move_down)
        self.remember_check.stateChanged.connect(self._on_remember_checked)
        self.table.activated.connect(self._on_open)
        self.table.selectionModel().currentRowChanged.connect(self._on_selection)

        self._on_selection()

    def _on_selection(self):
        index = self.table.currentIndex()
        self.delete_action.setEnabled(index.isValid())
        self.open_action.setEnabled(index.isValid())
        self.edit_action.setEnabled(index.isValid())
        self.move_up_action.setEnabled(index.isValid() and index.row() > 0)
        self.move_down_action.setEnabled(
            index.isValid() and index.row() < self.model.rowCount() - 1
        )

    def _on_new(self):
        self.dialog = ProjectCreate()
        self.dialog.setModal(True)
        self.dialog.project_saved.connect(self.model.add_project)
        self.dialog.exec()

    def _on_edit(self):
        row = self.table.currentIndex().row()
        project = self.model.projects[row]
        self.dialog = ProjectCreate(project)
        self.dialog.setModal(True)
        self.dialog.project_saved.connect(lambda p: self.model.update_project(row, p))
        self.dialog.exec()

    def _on_open(self):
        row = self.table.currentIndex().row()
        project = self.model.projects[row]
        self.ms.sm.transition("Load", main_state=self.ms, project=project)

    def _on_load_succeeded(self, game_state):
        if self.dialog:
            self.dialog.reset()

    def _on_load_error(self, error_info):
        if self.dialog:
            self.dialog.reset()

    def _on_load_cancel(self):
        self.thread_pool.cancel(self.worker)
        self.worker = None
        self.dialog = None

    def _on_delete(self):
        self.model.delete_project(self.table.currentIndex())

    def _on_move_up(self):
        new_row = self.model.move_up(self.table.currentIndex())
        self.table.selectRow(new_row)

    def _on_move_down(self):
        new_row = self.model.move_down(self.table.currentIndex())
        self.table.selectRow(new_row)

    def _on_remember_checked(self):
        self.ms.config.remember_project = self.remember_check.isChecked()
