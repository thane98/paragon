from PySide2.QtWidgets import QWidget
from services.service_locator import locator
from ui.autogen.ui_fe14_chapter_config_tab import Ui_fe14_chapter_config_tab
from ui.property_form import PropertyForm


class FE14ChapterConfigTab(Ui_fe14_chapter_config_tab, QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.chapter_data = None

        module_service = locator.get_scoped("ModuleService")
        config_module = module_service.get_common_module_template("Map Config")
        self.module = module_service.get_module("Chapters")
        self.header_property_form = PropertyForm(self.module.element_template)
        self.config_property_form = PropertyForm(config_module.element_template)
        self.header_property_form.editors["CID"].setEnabled(False)
        self.header_property_form.editors["Key (CID)"].setEnabled(False)
        self.scrollAreaWidgetContents.setLayout(self.header_property_form)
        self.scrollAreaWidgetContents_2.setLayout(self.config_property_form)
        self.splitter.setSizes([600, 200])

    def update_chapter_data(self, chapter_data):
        self.chapter_data = chapter_data
        chapter = self.chapter_data.chapter
        self.header_property_form.update_target(chapter)

        if self.chapter_data.config:
            self.scrollArea_2.setEnabled(True)
            config_element = self.chapter_data.config.element
            self.config_property_form.update_target(config_element)
        else:
            self.scrollArea_2.setEnabled(False)
            self.config_property_form.update_target(None)
