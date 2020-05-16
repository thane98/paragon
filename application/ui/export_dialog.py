import json
import logging

from PySide2 import QtWidgets, QtGui, QtCore
from PySide2.QtCore import QModelIndex
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QVBoxLayout, QTreeView, QFileDialog, QPushButton, QCheckBox, QMessageBox

from model.qt.export_changes_model import ExportChangesModel
from services.service_locator import locator
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
        self.remember_selections_checkbox = QCheckBox()
        self.remember_selections_checkbox.setText("Remember selections.")
        main_layout.addWidget(self.export_button)
        main_layout.addWidget(self.main_view)
        main_layout.addWidget(self.remember_selections_checkbox)
        self.setLayout(main_layout)

        self.main_view.expanded.connect(self._on_item_expanded)
        self.export_button.clicked.connect(self._on_export_triggered)
        self.remember_selections_checkbox.stateChanged.connect(self._on_remember_selections_state_changed)

        self._set_remember_checkbox_state_from_settings()

    def _set_remember_checkbox_state_from_settings(self):
        settings_service = locator.get_static("SettingsService")
        if settings_service.get_remember_exports():
            self.remember_selections_checkbox.setCheckState(QtCore.Qt.Checked)

    @staticmethod
    def _on_remember_selections_state_changed(state: int):
        should_remember = state == QtCore.Qt.Checked
        locator.get_static("SettingsService").set_remember_exports(should_remember)

    def closeEvent(self, event: QtGui.QCloseEvent):
        self.model.save_selected_items_tree()
        event.accept()

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
