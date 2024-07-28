from PySide6 import QtCore
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QTableWidget,
    QAbstractItemView,
    QTableView,
    QHeaderView,
    QTableWidgetItem,
    QStyle,
)


class ExaltScriptDiagnosticsTable(QTableWidget):
    diagnostic_selected = Signal(object)

    def __init__(self, game_data, parent=None):
        super().__init__(parent)

        self.game_data = game_data
        self.errors_by_file = {}
        self.warnings_by_file = {}

        self.setVisible(False)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setAlternatingRowColors(True)
        self.verticalHeader().hide()
        self.setMinimumHeight(150)

        self.activated.connect(self._on_row_selected)

    def update_diagnostics(self, analysis_result, script_node=None):
        new_errors_by_file = {}
        new_warnings_by_file = {}
        if script_node:
            if script_node in self.errors_by_file:
                del self.errors_by_file[script_node]
            if script_node in self.warnings_by_file:
                del self.warnings_by_file[script_node]
        for diagnostic in analysis_result.errors:
            if diagnostic.location:
                node = self.game_data.get_script_node_from_path(
                    diagnostic.location.file
                )
                file_results = new_errors_by_file.get(node, [])
                file_results.append(diagnostic)
                new_errors_by_file[node] = file_results
        for diagnostic in analysis_result.warnings:
            if diagnostic.location:
                node = self.game_data.get_script_node_from_path(
                    diagnostic.location.file
                )
                file_results = new_warnings_by_file.get(node, [])
                file_results.append(diagnostic)
                new_warnings_by_file[node] = file_results
        self.errors_by_file.update(new_errors_by_file)
        self.warnings_by_file.update(new_warnings_by_file)

    def clear_errors(self, script_node):
        if script_node in self.errors_by_file:
            del self.errors_by_file[script_node]

    def clear_warnings(self, script_node):
        if script_node in self.warnings_by_file:
            del self.warnings_by_file[script_node]

    def get_error_count(self) -> int:
        return sum(map(lambda r: len(r), self.errors_by_file.values()))

    def get_warning_count(self) -> int:
        return sum(map(lambda r: len(r), self.warnings_by_file.values()))

    def refresh(self):
        self.clear()
        all_errors = set()
        all_warnings = set()
        for diagnostic in self.errors_by_file.values():
            all_errors.update(diagnostic)
        for diagnostic in self.warnings_by_file.values():
            all_warnings.update(diagnostic)
        all_errors = sorted(
            all_errors,
            key=lambda d: (d.location.file, d.location.span) if d.location else None,
        )
        all_warnings = sorted(
            all_warnings,
            key=lambda d: (d.location.file, d.location.span) if d.location else None,
        )
        self.setRowCount(len(all_errors) + len(all_warnings))
        self.setColumnCount(5)

        self.setHorizontalHeaderLabels(["Type", "Message", "Line", "Index", "File"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        self.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )
        self.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeMode.ResizeToContents
        )

        for i, error in enumerate(all_errors):
            icon_item = QTableWidgetItem()
            icon_item.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical)
            )
            icon_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            icon_item.setData(QtCore.Qt.ItemDataRole.UserRole, error)
            self.setItem(i, 0, icon_item)
            self.setItem(i, 1, QTableWidgetItem(error.message))
            if error.location:
                self.setItem(i, 2, QTableWidgetItem(str(error.location.line_number)))
                self.setItem(i, 3, QTableWidgetItem(str(error.location.index_in_line)))
                self.setItem(
                    i,
                    4,
                    QTableWidgetItem(
                        error.location.file if error.location.file else ""
                    ),
                )
        for i, warning in enumerate(all_warnings):
            icon_item = QTableWidgetItem()
            icon_item.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
            )
            icon_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            icon_item.setData(QtCore.Qt.ItemDataRole.UserRole, warning)
            self.setItem(i + len(all_errors), 0, icon_item)
            self.setItem(i + len(all_errors), 1, QTableWidgetItem(warning.message))
            if warning.location:
                self.setItem(i, 2, QTableWidgetItem(str(warning.location.line_number)))
                self.setItem(
                    i, 3, QTableWidgetItem(str(warning.location.index_in_line))
                )
                self.setItem(
                    i,
                    4,
                    QTableWidgetItem(
                        warning.location.file if warning.location.file else ""
                    ),
                )

    def _on_row_selected(self):
        row = self.currentIndex().row()
        item = self.item(row, 0)
        if item:
            self.diagnostic_selected.emit(item.data(QtCore.Qt.ItemDataRole.UserRole))
