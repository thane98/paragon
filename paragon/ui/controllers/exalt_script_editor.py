from pathlib import Path
from typing import Optional

from PySide6 import QtGui
from PySide6.QtCore import QPoint, QModelIndex, QItemSelectionModel
from PySide6.QtWidgets import QStyle, QInputDialog

from paragon.model.exalt_script_proxy_model import ExaltScriptProxyModel
from paragon.model.main_state import MainState
from paragon.ui import utils
from paragon.ui.controllers.exalt_script_tab import (
    ExaltScriptAnalysisResult,
)
from paragon.ui.controllers.exalt_settings_editor import ExaltSettingsEditor
from paragon.ui.views.ui_exalt_script_editor import Ui_ExaltScriptEditor


class ExaltScriptEditor(Ui_ExaltScriptEditor):
    def __init__(self, main_state: MainState, game_data, parent=None):
        super().__init__(
            game_data, main_state.config.exalt_script_editor_config, parent
        )

        self.main_state = main_state
        self.game_data = game_data
        self.splitter_state = None
        self.selected_index: Optional[QModelIndex] = None
        self.config = main_state.config.exalt_script_editor_config

        self.settings_editor = ExaltSettingsEditor(self.config)

        self.model = ExaltScriptProxyModel(game_data, self.style())
        self.tree_view.setModel(self.model)

        self.settings_action.triggered.connect(self._on_settings_activated)
        self.compile_action.triggered.connect(self._on_compile)
        self.tree_view.customContextMenuRequested.connect(
            self._on_context_menu_requested
        )
        self.tree_view.activated.connect(self._on_script_activated)
        self.new_script_action.triggered.connect(self._on_new_script_activated)
        self.new_dir_action.triggered.connect(self._on_new_dir_activated)
        self.popup_button.clicked.connect(self._on_popup_button_pressed)
        self.table.diagnostic_selected.connect(self._on_error_or_warning_activated)
        self.search_line_edit.textChanged.connect(self._on_search_changed)

    def _on_compile(self):
        # Focus isn't transferred from the current tab when clicking the compile button, so force it to save here.
        for tab in self.tab_widget.tabs():
            tab.save()
        try:
            self.process_compile_result(self.game_data.compile_scripts())
        except:
            utils.error(self)

    def process_compile_result(self, result):
        self.table.update_diagnostics(
            ExaltScriptAnalysisResult(result.get_errors(), result.get_warnings())
        )
        self.errors_label.setText(f"Errors: {self.table.get_error_count()}")
        self.warnings_label.setText(f"Warnings: {self.table.get_warning_count()}")
        if not result.get_errors():
            self.status_bar.showMessage("Successfully compiled all files.", 5000)
        else:
            self.status_bar.showMessage("Encountered errors while compiling.", 5000)
            if not self.table.isVisible():
                self._on_popup_button_pressed()

    def has_errors(self) -> bool:
        return bool(self.table.get_error_count())

    def _on_context_menu_requested(self, point: QPoint):
        index = self.tree_view.indexAt(point)
        data = self.model.data_at(index)
        if data and not data.node:
            if data.node_kind != "standard_library":
                self.directory_item_menu.popup(
                    self.tree_view.viewport().mapToGlobal(point)
                )
                self.selected_index = index

    def _on_settings_activated(self):
        self.settings_editor.exec()
        self.tab_widget.refresh_settings()

    def _on_new_script_activated(self):
        if self.selected_index:
            text, ok = QInputDialog.getText(self, "Input Script Name", "Script Name")
            if not ok:
                return
            if not len(Path(text).parts) == 1:
                return
            try:
                self.model.add_new_script(self.selected_index, text)
            except:
                utils.error(self)

    def _on_new_dir_activated(self):
        if self.selected_index:
            text, ok = QInputDialog.getText(self, "Input Script Name", "Script Name")
            if not ok:
                return
            if not len(Path(text).parts) == 1:
                return
            try:
                self.model.add_new_dir(self.selected_index, text)
            except:
                utils.error(self)

    def _on_search_changed(self, text: str):
        self.model.setFilterFixedString(text)

    def _on_script_activated(self, index: QModelIndex):
        data = self.model.data_at(index)
        if data and data.node:
            try:
                self.tab_widget.open_script(data.node, self._handle_analysis)
            except:
                utils.error(self)

    def _handle_analysis(self, result: ExaltScriptAnalysisResult):
        if tab := self.tab_widget.current_tab():
            self.table.update_diagnostics(result, tab.script_node)
            self.errors_label.setText(f"Errors: {self.table.get_error_count()}")
            self.warnings_label.setText(f"Warnings: {self.table.get_warning_count()}")
            self.table.refresh()

    def _on_popup_button_pressed(self):
        if self.table.isVisible():
            self.splitter_state = self.editor_splitter.saveState()
            self.table.hide()
            self.editor_splitter.setSizes([self.editor_splitter.sizes()[0], 0])
            self.editor_splitter.handle(1).setEnabled(False)
            self.editor_splitter.handle(1).setCursor(QtGui.Qt.CursorShape.ArrowCursor)
            self.popup_button.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp)
            )
        else:
            if self.splitter_state:
                self.editor_splitter.restoreState(self.splitter_state)
            self.editor_splitter.handle(1).setEnabled(True)
            self.editor_splitter.handle(1).setCursor(QtGui.Qt.CursorShape.SizeVerCursor)
            self.table.show()
            self.popup_button.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown)
            )

    def _on_error_or_warning_activated(self, diagnostic):
        if diagnostic.location:
            node = self.game_data.get_script_node_from_path(diagnostic.location.file)
            if index := self.model.index_of(node.path, node.kind()):
                self.tree_view.expand(index.parent())
                self.tree_view.selectionModel().select(
                    index, QItemSelectionModel.SelectionFlag.SelectCurrent
                )
                self._on_script_activated(index)
                if tab := self.tab_widget.current_tab():
                    tab.jump_to_location(diagnostic.location)
