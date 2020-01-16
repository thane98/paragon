from PySide2 import QtCore
from PySide2.QtCore import QSortFilterProxyModel
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget
from services.service_locator import locator
from ui.autogen.ui_fe14_chapter_editor import Ui_fe14_chapter_editor
from ui.fe14_chapter_characters_tab import FE14ChapterCharactersTab
from ui.fe14_chapter_config_tab import FE14ChapterConfigTab
from ui.fe14_chapter_spawns_tab import FE14ChapterSpawnsTab


class FE14ChapterEditor(Ui_fe14_chapter_editor, QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Chapter Editor")
        self.setWindowIcon(QIcon("paragon.ico"))

        driver = locator.get_scoped("Driver")
        self.chapter_module = driver.modules["Chapters"]
        self.config_tab = FE14ChapterConfigTab()
        self.spawns_tab = FE14ChapterSpawnsTab()
        self.characters_tab = FE14ChapterCharactersTab()

        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.chapter_module.entries_model)
        self.list_view.setModel(self.proxy_model)

        self.tab_widget.addTab(self.config_tab, "Config")
        self.tab_widget.addTab(self.spawns_tab, "Map")
        self.tab_widget.addTab(self.characters_tab, "Characters")

        self.search_field.textChanged.connect(self._update_filter)
        self.list_view.selectionModel().currentRowChanged.connect(self._update_selection)

    def _update_filter(self):
        self.proxy_model.setFilterRegExp(self.search_field.text())

    def _update_selection(self, index):
        service = locator.get_scoped("ChapterService")
        chapter = self.proxy_model.data(index, QtCore.Qt.UserRole)
        chapter_data = service.get_chapter_data_from_chapter(chapter)

        self.config_tab.update_chapter_data(chapter_data)
        self.spawns_tab.update_chapter_data(chapter_data)
        self.characters_tab.update_chapter_data(chapter_data)
