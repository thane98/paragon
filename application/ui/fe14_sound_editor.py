from typing import Optional

from PySide2 import QtCore
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget

from model.qt.voice_set_model import VoiceSetEntriesModel
from module.properties.property_container import PropertyContainer
from services.service_locator import locator
from ui.autogen.ui_sound_editor import Ui_sound_editor
from ui.property_form import PropertyForm


class FE14SoundEditor(QWidget, Ui_sound_editor):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Voice Set Editor")
        self.setWindowIcon(QIcon("paragon.ico"))

        self.service = locator.get_scoped("SoundService")
        self.voice_set_model = self.service.get_voice_set_model()
        self.form = PropertyForm(self.service.template)
        widget = QWidget()
        widget.setLayout(self.form)
        self.horizontalLayout_3.addWidget(widget)

        self.sets_list_view.setModel(self.service.get_voice_set_model())
        self.sets_list_view.selectionModel().currentRowChanged.connect(self._update_set_selection)
        self.form.editors["Name"].editingFinished.connect(self._write_back_entry)
        self.form.editors["Tag"].editingFinished.connect(self._write_back_entry)

        self.selected_voice_set: Optional[VoiceSetEntriesModel] = None
        self.selected_voice_set_entry: Optional[PropertyContainer] = None

    def show(self):
        super().show()

    def _update_set_selection(self, index: QtCore.QModelIndex):
        if self.selected_voice_set:
            self.sounds_list_view.selectionModel().currentRowChanged.disconnect()
        self.selected_voice_set = self.voice_set_model.data(index, QtCore.Qt.UserRole)
        self.sounds_list_view.setModel(self.selected_voice_set)

        if self.selected_voice_set:
            self.sounds_list_view.selectionModel().currentRowChanged.connect(self._update_sound_selection)
        self.selected_voice_set_entry = None
        self.form.update_target(self.selected_voice_set_entry)

    def _update_sound_selection(self, index: QtCore.QModelIndex):
        self.selected_voice_set_entry = self.selected_voice_set.data(index, QtCore.Qt.UserRole)
        self.form.update_target(self.selected_voice_set_entry)

    def _write_back_entry(self):
        if self.selected_voice_set and self.selected_voice_set_entry:
            self.selected_voice_set.save_entry(self.selected_voice_set_entry)
