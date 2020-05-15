import json
import logging

from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import QModelIndex
from PySide2.QtGui import QContextMenuEvent, QIcon
from PySide2.QtWidgets import QWidget, QVBoxLayout, QTreeView, QFileDialog, QPushButton

from model.qt.export_changes_model import ExportChangesModel
from ui.error_dialog import ErrorDialog


class ExportDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = ExportChangesModel()
        self.error_dialog = None
        self.setWindowIcon(QIcon("paragon.ico"))
        self.setWindowTitle("Export")

        main_layout = QVBoxLayout(self)
        self.export_button = QPushButton()
        self.export_button.setText("Export")
        self.main_view = QTreeView()
        self.main_view.setModel(self.model)
        self.main_view.setHeaderHidden(True)
        self.main_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        main_layout.addWidget(self.export_button)
        main_layout.addWidget(self.main_view)
        self.setLayout(main_layout)

        self.main_view.expanded.connect(self._on_item_expanded)
        self.export_button.clicked.connect(self._on_export_triggered)

    def _on_export_triggered(self):
        file_name, ok = QFileDialog.getSaveFileName(
            self,
            caption="Select Changes File Destination",
            filter="*.json"
        )
        if ok:
            self._try_export_and_write(file_name)

    def _try_export_and_write(self, file_name):
        logging.debug("Exporting selected data to %s" % file_name)
        try:
            export_data = self.model.export_selected_items()
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=4, ensure_ascii=False)
        except:
            logging.exception("An error occurred while exporting data.")
            self.error_dialog = ErrorDialog("An error occurred while exporting. See the log for details.")
            self.error_dialog.show()

    def _on_item_expanded(self, index: QModelIndex):
        self.model.update_data_for_index(index)
