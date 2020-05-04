from typing import List

from PySide2.QtCore import QModelIndex
from PySide2.QtGui import QStandardItemModel, QStandardItem

from model.project import Project


class ProjectModel(QStandardItemModel):
    def __init__(self, projects: List[Project], parent=None):
        super().__init__(parent)
        self.projects = projects
        self._populate_model()
        self.setHorizontalHeaderLabels(["Project Path", "Game", "Language"])

    def _populate_model(self):
        for project in self.projects:
            self.appendRow(self._create_row_from_project(project))

    def add_project(self, project: Project):
        self.projects.append(project)
        self.appendRow(self._create_row_from_project(project))

    def remove_project(self, index: QModelIndex):
        del self.projects[index.row()]
        self.removeRow(index.row())

    def move_project_up(self, index: QModelIndex) -> int:
        row_number = index.row()
        if row_number == 0:
            return row_number
        row = self.takeRow(row_number)
        self.insertRow(row_number - 1, row)
        self.projects[row_number - 1], self.projects[row_number] = \
            self.projects[row_number], self.projects[row_number - 1]
        return row_number - 1

    def move_project_down(self, index: QModelIndex) -> int:
        row_number = index.row()
        if row_number == self.rowCount() - 1:
            return row_number
        row = self.takeRow(row_number)
        self.insertRow(row_number + 1, row)
        self.projects[row_number + 1], self.projects[row_number] = \
            self.projects[row_number], self.projects[row_number + 1]
        return row_number + 1

    @staticmethod
    def _create_row_from_project(project: Project) -> List[QStandardItem]:
        item = QStandardItem(project.patch_path)
        item.setText(project.patch_path)
        item.setData(project)
        game_item = QStandardItem(project.get_game_name())
        language_item = QStandardItem(project.get_language_name())
        return [item, game_item, language_item]
