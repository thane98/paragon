import logging
from typing import Optional

from PySide2 import QtCore
from PySide2.QtCore import QPoint, QModelIndex
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QMenu, QAction, QInputDialog

from model.qt.voice_set_model import VoiceSetEntriesModel
from module.properties.property_container import PropertyContainer
from services.service_locator import locator
from ui.autogen.ui_sound_editor import Ui_sound_editor
from ui.error_dialog import ErrorDialog
from ui.property_form import PropertyForm


class FE14SoundEditor(QWidget, Ui_sound_editor):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Voice Set Editor")
        self.setWindowIcon(QIcon("paragon.ico"))

        self.service = locator.get_scoped("SoundService")
        self.voice_set_model = self.service.get_voice_set_model()
        self.error_dialog = None
        self.form = PropertyForm(self.service.template)
        widget = QWidget()
        widget.setLayout(self.form)
        self.horizontalLayout_3.addWidget(widget)

        self.proxy_model = QtCore.QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.voice_set_model)

        self.sets_menu = QMenu(self)
        self.add_set_action = QAction("Add Voice Set")
        self.remove_set_action = QAction("Remove Voice Set")
        self.remove_set_action.setDisabled(True)
        self.sets_menu.addActions([self.add_set_action, self.remove_set_action])
        self.sets_list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.sets_list_view.customContextMenuRequested.connect(self._on_sets_menu_requested)

        self.entries_menu = QMenu(self)
        self.entries_menu.setDisabled(True)
        self.add_entry_action = QAction("Add Entry")
        self.remove_entry_action = QAction("Remove Entry")
        self.copy_tag_action = QAction("Copy Tag to All Entries")
        self.entries_menu.addActions([self.add_entry_action, self.remove_entry_action, self.copy_tag_action])
        self.sounds_list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.sounds_list_view.customContextMenuRequested.connect(self._on_entries_menu_requested)

        self.sets_list_view.setModel(self.proxy_model)
        self.sets_list_view.selectionModel().currentRowChanged.connect(self._update_set_selection)
        self.search_bar.textChanged.connect(self._update_filter)
        self.add_set_action.triggered.connect(self._on_add_set_triggered)
        self.remove_set_action.triggered.connect(self._on_remove_set_triggered)
        self.add_entry_action.triggered.connect(self._on_add_entry_triggered)
        self.remove_entry_action.triggered.connect(self._on_remove_entry_triggered)
        self.copy_tag_action.triggered.connect(self._on_copy_tags_triggered)
        self.form.editors["Name"].editingFinished.connect(self._write_back_entry)
        self.form.editors["Tag"].editingFinished.connect(self._write_back_entry)

        self.selected_voice_set: Optional[VoiceSetEntriesModel] = None
        self.selected_voice_set_entry: Optional[PropertyContainer] = None

        self.service.set_in_use()

    def show(self):
        super().show()
        self.setDisabled(not self.service.load_succeeded)
        if not self.service.load_succeeded:
            self.error_dialog = ErrorDialog("Unable to load required data. See the log for details.")
            self.error_dialog.show()

    def _update_filter(self):
        self.proxy_model.setFilterRegExp(self.search_bar.text())

    def _on_entries_menu_requested(self, point: QPoint):
        self.entries_menu.exec_(self.sounds_list_view.mapToGlobal(point))

    def _on_sets_menu_requested(self, point: QPoint):
        self.sets_menu.exec_(self.sets_list_view.mapToGlobal(point))

    def _update_set_selection(self, index: QtCore.QModelIndex):
        if self.selected_voice_set:
            self.sounds_list_view.selectionModel().currentRowChanged.disconnect()
        self.selected_voice_set = self.proxy_model.data(index, QtCore.Qt.UserRole)
        self.sounds_list_view.setModel(self.selected_voice_set)

        if self.selected_voice_set:
            self.sounds_list_view.selectionModel().currentRowChanged.connect(self._update_sound_selection)
            self.entries_menu.setDisabled(False)
            self.remove_set_action.setDisabled(False)
        else:
            self.entries_menu.setDisabled(True)
            self.remove_set_action.setDisabled(True)
        self.remove_entry_action.setDisabled(True)
        self.copy_tag_action.setDisabled(True)
        self.selected_voice_set_entry = None
        self.form.update_target(self.selected_voice_set_entry)

    def _update_sound_selection(self, index: QtCore.QModelIndex):
        self.selected_voice_set_entry = self.selected_voice_set.data(index, QtCore.Qt.UserRole)
        self.remove_entry_action.setDisabled(self.selected_voice_set_entry is None)
        self.copy_tag_action.setDisabled(self.selected_voice_set_entry is None)
        self.form.update_target(self.selected_voice_set_entry)

    def _write_back_entry(self):
        if self.selected_voice_set and self.selected_voice_set_entry:
            self.selected_voice_set.save_entry(self.selected_voice_set_entry)

    def _on_add_entry_triggered(self):
        if self.selected_voice_set:
            self.selected_voice_set.insertRow(self.selected_voice_set.rowCount())

    def _on_remove_entry_triggered(self):
        if self.selected_voice_set and self.selected_voice_set_entry:
            self.selected_voice_set.remove_entry(self.selected_voice_set_entry)
            self.sounds_list_view.selectionModel().clearCurrentIndex()

    def _on_copy_tags_triggered(self):
        if self.selected_voice_set and self.selected_voice_set_entry:
            self.selected_voice_set.synchronize_tags(self.selected_voice_set_entry)

    def _on_add_set_triggered(self):
        (desired_name, ok) = QInputDialog.getText(self, "Enter a unique name for the voice set.", "Name")
        if not ok:
            return
        try:
            self.voice_set_model.create_voice_set(desired_name)
        except NameError:
            self.error_dialog = ErrorDialog("Voice set name %s is already in use." % desired_name)
            self.error_dialog.show()
        except:
            logging.exception("Unknown error when adding voice set to IndirectSound.")
            self.error_dialog = ErrorDialog("An unknown error occurred. See the log for details.")
            self.error_dialog.show()

    def _on_remove_set_triggered(self):
        if self.selected_voice_set:
            self.voice_set_model.remove_voice_set(self.selected_voice_set.voice_set_label)
            self.sets_list_view.clearSelection()
