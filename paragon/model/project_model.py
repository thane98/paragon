from typing import List

from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QStandardItemModel, QStandardItem

from paragon.model.project import Project


class ProjectModel(QStandardItemModel):
    def __init__(self, projects: List[Project]):
        super().__init__()
        self.projects = projects
        self.setHorizontalHeaderLabels(["Name", "Game", "Language", "Output Path"])
        for project in projects:
            self.appendRow(self.create_row(project))

    def add_project(self, project):
        self.appendRow(self.create_row(project))
        self.projects.append(project)

    def delete_project(self, index: QModelIndex):
        if index.isValid():
            self.removeRow(index.row())
            del self.projects[index.row()]

    def update_project(self, row, project):
        self.takeRow(row)
        self.insertRow(row, ProjectModel.create_row(project))
        self.projects[row] = project

    def move_up(self, index: QModelIndex):
        row_number = index.row()
        if row_number == 0:
            return row_number
        row = self.takeRow(row_number)
        self.insertRow(row_number - 1, row)
        self.projects[row_number - 1], self.projects[row_number] = (
            self.projects[row_number],
            self.projects[row_number - 1],
        )
        return row_number - 1

    def move_down(self, index: QModelIndex):
        row_number = index.row()
        if row_number == self.rowCount() - 1:
            return row_number
        row = self.takeRow(row_number)
        self.insertRow(row_number + 1, row)
        self.projects[row_number + 1], self.projects[row_number] = (
            self.projects[row_number],
            self.projects[row_number + 1],
        )
        return row_number + 1

    @staticmethod
    def create_row(project: Project) -> List[QStandardItem]:
        item = QStandardItem()
        item.setText(project.name)
        item.setData(project)
        game_item = QStandardItem(project.game.value)
        language_item = QStandardItem(project.language.value)
        output_path_item = QStandardItem(project.output_path)
        return [item, game_item, language_item, output_path_item]
