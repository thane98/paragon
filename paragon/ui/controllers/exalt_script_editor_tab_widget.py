import typing
from pathlib import Path
from typing import Optional

from PySide6 import QtCore
from PySide6.QtWidgets import QTabWidget

from paragon.model.exalt_script_editor_config import ExaltScriptEditorConfig
from paragon.ui.controllers.exalt_script_tab import ExaltScriptTab


class ExaltScriptEditorTabWidget(QTabWidget):
    def __init__(self, game_data, config: ExaltScriptEditorConfig, parent=None):
        super().__init__(parent)

        self.setTabsClosable(True)
        self.setMovable(True)

        self.game_data = game_data
        self.config = config

        self.tabCloseRequested.connect(lambda index: self.removeTab(index))
        self.currentChanged.connect(self._on_current_changed)

    def _on_current_changed(self):
        if tab := self.current_tab():
            tab.analyze()

    def refresh_settings(self):
        for i in range(0, self.count()):
            tab: ExaltScriptTab = typing.cast(Optional[ExaltScriptTab], self.widget(i))
            tab.refresh_settings()

    def open_script(self, script_node, on_analyze) -> ExaltScriptTab:
        tab_for_path = self.find_tab_by_script_path(script_node.path)
        if tab_for_path:
            (index, tab) = tab_for_path
            self.setCurrentIndex(index)
            return tab
        if tab := self.current_tab():
            tab.cancel_analysis()
        tab = ExaltScriptTab(self.game_data, self.config, script_node)
        tab.analysis_complete.connect(
            on_analyze, QtCore.Qt.ConnectionType.UniqueConnection
        )
        self.addTab(tab, Path(script_node.path).name)
        self.setTabToolTip(self.count() - 1, script_node.path)
        self.setCurrentIndex(self.count() - 1)
        return tab

    def find_tab_by_script_path(
        self, path: str
    ) -> Optional[typing.Tuple[int, ExaltScriptTab]]:
        for i in range(0, self.count()):
            tab: ExaltScriptTab = typing.cast(Optional[ExaltScriptTab], self.widget(i))
            if tab.script_path == path:
                return i, tab
        return None

    def current_tab(self) -> Optional[ExaltScriptTab]:
        return typing.cast(Optional[ExaltScriptTab], self.currentWidget())

    def tabs(self) -> typing.Iterator[ExaltScriptTab]:
        for i in range(0, self.count()):
            yield typing.cast(Optional[ExaltScriptTab], self.widget(i))
