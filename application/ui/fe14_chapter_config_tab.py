from PySide2 import QtWidgets
from PySide2.QtWidgets import QWidget

from services.service_locator import locator
from ui.autogen.ui_fe14_chapter_config_tab import Ui_fe14_chapter_config_tab


class FE14ChapterConfigTab(Ui_fe14_chapter_config_tab, QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.chapter_data = None

        driver = locator.get_scoped("Driver")
        self.module = driver.modules["Chapters"]
        self.header_editors = []
        template = self.module.element_template
        for (key, prop) in template.items():
            label = QtWidgets.QLabel(key)
            editor = prop.create_editor()
            if editor:
                self.header_editors.append(editor)
                self.header_form.addRow(label, editor)
        self.header_editors[0].setEnabled(False)
        self.header_editors[1].setEnabled(False)

        config_module = driver.common_modules["Map Config"]
        self.config_editors = []
        template = config_module.element_template
        for (key, prop) in template.items():
            label = QtWidgets.QLabel(key)
            editor = prop.create_editor()
            if editor:
                self.config_editors.append(editor)
                self.config_form.addRow(label, editor)

    def update_chapter_data(self, chapter_data):
        self.chapter_data = chapter_data
        chapter = self.chapter_data.chapter
        for editor in self.header_editors:
            editor.update_target(chapter)

        if self.chapter_data.config:
            self.scrollArea_2.setEnabled(True)
            config_element = self.chapter_data.config.element
            for editor in self.config_editors:
                editor.update_target(config_element)
        else:
            self.scrollArea_2.setEnabled(False)
