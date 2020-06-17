from PySide2 import QtCore
from PySide2.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSplitter

from services.service_locator import locator
from ui.property_form import PropertyForm
from ui.widgets.fe14_chapter_text_data_widget import FE14ChapterTextDataWidget


class FE14ChapterConfigTab(QScrollArea):
    def __init__(self):
        super().__init__()
        self.chapter_data = None
        module_service = locator.get_scoped("ModuleService")
        config_module = module_service.get_common_module_template("Map Config")
        self.module = module_service.get_module("Chapters")
        self.text_data_widget = FE14ChapterTextDataWidget()
        self.header_scroll, self.header_property_form = PropertyForm.create_with_scroll(self.module.element_template)
        self.config_scroll, self.config_property_form = PropertyForm.create_with_scroll(config_module.element_template)
        self.header_property_form.editors["CID"].setEnabled(False)
        self.header_property_form.editors["Key (CID)"].setEnabled(False)
        self.vertical_layout = QVBoxLayout(parent=self)
        self.splitter = QSplitter(parent=self)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter2 = QSplitter(parent=self)
        self.splitter2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.text_data_widget)
        self.splitter.addWidget(self.splitter2)
        self.splitter2.addWidget(self.header_scroll)
        self.splitter2.addWidget(self.config_scroll)
        self.vertical_layout.addWidget(self.splitter)
        self.scroll_content = QWidget()
        self.scroll_content.setLayout(self.vertical_layout)
        self.setWidget(self.scroll_content)
        self.setWidgetResizable(True)

    def update_chapter_data(self, chapter_data):
        self.chapter_data = chapter_data
        chapter_header = chapter_data.chapter if chapter_data else None
        config = chapter_data.config.element if chapter_data else None
        self.text_data_widget.update_chapter_data(chapter_data)
        self.header_property_form.update_target(chapter_header)
        self.config_property_form.update_target(config)
        self.header_scroll.setEnabled(chapter_header is not None)
        self.config_scroll.setEnabled(config is not None)
