from PySide2 import QtCore
from PySide2.QtCore import QSortFilterProxyModel
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QInputDialog, QErrorMessage
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
        self.remove_button.setEnabled(False)
        self.message_dialog = QErrorMessage()

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
        self.add_button.clicked.connect(self._on_add_chapter_pressed)

    def _update_filter(self):
        self.proxy_model.setFilterRegExp(self.search_field.text())

    def _update_selection(self, index):
        service = locator.get_scoped("ChapterService")
        chapter = self.proxy_model.data(index, QtCore.Qt.UserRole)
        chapter_data = service.get_chapter_data_from_chapter(chapter)

        self.config_tab.update_chapter_data(chapter_data)
        self.spawns_tab.update_chapter_data(chapter_data)
        self.characters_tab.update_chapter_data(chapter_data)

    def _on_add_chapter_pressed(self):
        # Get the chapter to use as a base
        choices = self._create_chapter_choice_list()
        (choice, ok) = QInputDialog.getItem(self, "Select Base Chapter", "Base Chapter", choices)
        if not ok:
            return
        source_chapter = self._get_chapter_from_choice(choice, choices)

        # Get the desired CID.
        (desired_cid, ok) = QInputDialog.getText(self, "Enter a CID for the new chapter.", "CID")
        if not ok:
            return

        # Validate the CID.
        service = locator.get_scoped("ChapterService")
        if service.is_cid_in_use(desired_cid):
            self.message_dialog.showMessage("The CID \"" + desired_cid + "\" is already in use.")
            return

        # Create the chapter
        service.create_chapter(source_chapter, desired_cid)

    def _create_chapter_choice_list(self):
        choices = []
        for i in range(0, len(self.chapter_module.entries)):
            chapter = self.chapter_module.entries[i]
            cid = chapter["CID"].value
            choices.append(str(i) + ". " + cid)
        return choices

    def _get_chapter_from_choice(self, choice, choices_list):
        for i in range(0, len(choices_list)):
            if choice == choices_list[i]:
                return self.chapter_module.entries[i]
        raise ValueError
