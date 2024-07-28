from PySide6 import QtGui, QtCore
from PySide6.QtGui import (
    QIcon,
    QAction,
)
from PySide6.QtWidgets import (
    QListWidget,
    QSplitter,
    QStatusBar,
    QLabel,
    QLineEdit,
    QPushButton,
    QStyle,
    QTreeWidget,
    QMenu,
    QTreeView,
    QAbstractItemView,
    QToolBar,
)

from paragon.model.exalt_script_editor_config import ExaltScriptEditorConfig
from paragon.ui.controllers.exalt_script_diagnostics_table import (
    ExaltScriptDiagnosticsTable,
)
from paragon.ui.controllers.exalt_script_editor_tab_widget import (
    ExaltScriptEditorTabWidget,
)
from paragon.ui.views import layouts


class Ui_ExaltScriptEditor(QSplitter):
    def __init__(self, game_data, config: ExaltScriptEditorConfig, parent=None):
        super().__init__(parent)

        self.new_script_action = QAction("New Script")
        self.new_dir_action = QAction("New Directory")

        self.directory_item_menu = QMenu()
        self.directory_item_menu.addActions(
            [self.new_script_action, self.new_dir_action]
        )

        self.search_line_edit = QLineEdit()
        self.search_line_edit.setPlaceholderText("Search...")
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.tree_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)

        self.table = ExaltScriptDiagnosticsTable(game_data)
        popup_layout = layouts.make_vbox([self.table])

        self.tab_widget = ExaltScriptEditorTabWidget(game_data, config)

        self.tool_bar = QToolBar()
        self.settings_action = QAction("Settings")
        self.compile_action = QAction("Compile")
        self.tool_bar.addActions([self.settings_action, self.compile_action])

        self.editor_splitter = QSplitter()
        self.editor_splitter.setChildrenCollapsible(False)
        self.editor_splitter.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.editor_splitter.addWidget(self.tab_widget)
        self.editor_splitter.addWidget(layouts.wrap_layout(popup_layout))
        self.editor_splitter.setStretchFactor(0, 1)
        self.editor_splitter.handle(1).setEnabled(False)
        self.editor_splitter.handle(1).setCursor(QtGui.Qt.CursorShape.ArrowCursor)

        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp)
        self.popup_button = QPushButton("Diagnostics")
        self.popup_button.setIcon(QIcon(icon))
        self.errors_label = QLabel()
        self.warnings_label = QLabel()
        self.status_bar.addPermanentWidget(self.popup_button)
        self.status_bar.addWidget(self.errors_label)
        self.status_bar.addWidget(self.warnings_label)

        right_layout = layouts.make_vbox(
            [self.tool_bar, self.editor_splitter, self.status_bar], spacing=0
        )

        self.addWidget(
            layouts.wrap_layout(
                layouts.make_vbox([self.search_line_edit, self.tree_view])
            )
        )
        self.addWidget(layouts.wrap_layout(right_layout))
        self.setStretchFactor(1, 1)
        self.resize(1000, 800)

        self.setWindowTitle("Paragon - Script Editor")
        self.setWindowIcon(QIcon("paragon.ico"))
