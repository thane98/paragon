from PySide2 import QtCore
from PySide2.QtWidgets import QWidget, QFormLayout, QLabel, QLineEdit, QVBoxLayout, QScrollArea, QSplitter

from model.fe14.chapter_data import CHAPTER_DIALOGUES
from services.service_locator import locator
from ui.property_form import PropertyForm


class FE14ChapterConfigTab(QScrollArea):
    def __init__(self):
        super().__init__()
        self.chapter_data = None

        self.message_data_form = QFormLayout()
        self.message_data_editors = []
        for dialogue in CHAPTER_DIALOGUES:
            label = QLabel(dialogue.name)
            editor = QLineEdit()
            index = len(self.message_data_editors)
            editor.editingFinished.connect(lambda i=index, e=editor: self._on_dialogue_editor_text_changed(i, e.text()))
            self.message_data_editors.append(editor)
            self.message_data_form.addRow(label, editor)

        module_service = locator.get_scoped("ModuleService")
        config_module = module_service.get_common_module_template("Map Config")
        self.module = module_service.get_module("Chapters")
        self.header_property_form = PropertyForm(self.module.element_template)
        self.config_property_form = PropertyForm(config_module.element_template)
        self.header_property_form.editors["CID"].setEnabled(False)
        self.header_property_form.editors["Key (CID)"].setEnabled(False)

        self.vertical_layout = QVBoxLayout(parent=self)
        self.message_data_scroll = QScrollArea()
        self.message_data_scroll.setWidgetResizable(True)
        self.message_data_scroll_content = QWidget()
        self.message_data_scroll_content.setLayout(self.message_data_form)
        self.message_data_scroll.setWidget(self.message_data_scroll_content)
        self.header_scroll = QScrollArea()
        self.header_scroll.setWidgetResizable(True)
        self.header_scroll_content = QWidget()
        self.header_scroll_content.setLayout(self.header_property_form)
        self.header_scroll.setWidget(self.header_scroll_content)
        self.config_scroll = QScrollArea()
        self.config_scroll.setWidgetResizable(True)
        self.config_scroll_content = QWidget()
        self.config_scroll_content.setLayout(self.config_property_form)
        self.config_scroll.setWidget(self.config_scroll_content)
        self.splitter = QSplitter(parent=self)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.addWidget(self.message_data_scroll)
        self.splitter.addWidget(self.header_scroll)
        self.splitter.addWidget(self.config_scroll)
        self.vertical_layout.addWidget(self.splitter)
        self.scroll_content = QWidget()
        self.scroll_content.setLayout(self.vertical_layout)
        self.setWidget(self.scroll_content)
        self.setWidgetResizable(True)

    def update_chapter_data(self, chapter_data):
        self.chapter_data = chapter_data
        chapter = self.chapter_data.chapter
        self.header_property_form.update_target(chapter)

        if self.chapter_data.config:
            self.config_scroll.setEnabled(True)
            config_element = self.chapter_data.config.element
            self.config_property_form.update_target(config_element)
            self._update_message_data_editors(self.chapter_data.message_data)
        else:
            self.config_scroll.setEnabled(False)
            self.config_property_form.update_target(None)
            self._update_message_data_editors(None)

    def _update_message_data_editors(self, message_data):
        if not message_data:
            for editor in self.message_data_editors:
                editor.setText("")
            self.message_data_scroll.setEnabled(False)
        else:
            for i in range(0, len(self.message_data_editors)):
                editor = self.message_data_editors[i]
                new_value = self.chapter_data.message_data[i]
                editor.setText(new_value)
            self.message_data_scroll.setEnabled(True)

    def _on_dialogue_editor_text_changed(self, index: int, new_value: str):
        if self.chapter_data and self.chapter_data.message_data:
            self.chapter_data.message_data[index] = new_value
