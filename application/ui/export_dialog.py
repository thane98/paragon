from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import QModelIndex
from PySide2.QtGui import QContextMenuEvent
from PySide2.QtWidgets import QWidget, QVBoxLayout, QTreeView, QFileDialog, QPushButton

from model.qt.export_changes_model import ExportChangesModel


class ExportDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = ExportChangesModel()

        main_layout = QVBoxLayout(self)
        self.export_button = QPushButton()
        self.export_button.setText("Export")
        self.main_view = QTreeView()
        self.main_view.installEventFilter(self)
        self.main_view.setModel(self.model)
        self.main_view.setHeaderHidden(True)
        self.main_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        main_layout.addWidget(self.export_button)
        main_layout.addWidget(self.main_view)
        self.setLayout(main_layout)

        self.main_view.expanded.connect(self._on_item_expanded)
        self.export_button.clicked.connect(self._on_export_triggered)

    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if watched == self.main_view and issubclass(type(event), QContextMenuEvent):
            index = self.main_view.indexAt(event.pos())
            item = self.model.itemFromIndex(index)
            if item:
                self.model.update_delete_state(item)
            return True
        return False

    def _on_export_triggered(self):
        self.model.export_selected_items()
        # file_name, ok = QFileDialog.getSaveFileName(
        #     self,
        #     caption="Select Changes File Destination",
        #     filter="*.json"
        # )
        # if ok:
        #     pass

    def _on_item_expanded(self, index: QModelIndex):
        self.model.update_data_for_index(index)
