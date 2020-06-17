from typing import Optional

from PySide2 import QtCore
from PySide2.QtCore import QSortFilterProxyModel, QModelIndex
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QInputDialog

from model.fe14.chapter_data import ChapterData
from services.service_locator import locator
from ui.error_dialog import ErrorDialog
from ui.views.ui_fe14_chapter_editor import Ui_FE14ChapterEditor


class FE14ChapterEditor(Ui_FE14ChapterEditor):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chapter Editor")
        self.setWindowIcon(QIcon("paragon.ico"))
        self.error_dialog = None

        module_service = locator.get_scoped("ModuleService")
        self.chapter_module = module_service.get_module("Chapters")
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.chapter_module.entries_model)
        self.proxy_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.chapter_list_view.setModel(self.proxy_model)

        self.chapter_search_bar.textChanged.connect(self._update_filter)
        self.chapter_list_view.selectionModel().currentRowChanged.connect(self._update_selection)
        self.add_chapter_action.triggered.connect(self._on_add_chapter_triggered)
        self.hide_selector_action.triggered.connect(self._on_toggle_selector_triggered)

        self._update_selection(QModelIndex())

    def _update_filter(self):
        self.proxy_model.setFilterRegExp(self.search_field.text())

    def _update_selection(self, index):
        service = locator.get_scoped("ChapterService")
        data = self.proxy_model.data(index, QtCore.Qt.UserRole)
        chapter_data: Optional[ChapterData] = service.get_chapter_data_from_chapter(data) if data else None
        person_module = chapter_data.person if chapter_data else None
        message_archive = chapter_data.conversation_data if chapter_data else None
        self.config_tab.update_chapter_data(chapter_data)
        self.map_tab.update_chapter_data(chapter_data)
        self.characters_tab.set_module(person_module)
        self.conversation_tab.set_archive(message_archive)

    def _on_add_chapter_triggered(self):
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
            self.error_dialog = ErrorDialog("The CID \"" + desired_cid + "\" is already in use.")
            self.error_dialog.show()
            return
        if not desired_cid.startswith("CID_"):
            self.error_dialog = ErrorDialog("CID must start with the \"CID_\"")
            self.error_dialog.show()
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

    def _on_toggle_selector_triggered(self):
        self.selector_widget.setVisible(not self.selector_widget.isVisible())
        self.visual_splitter.setVisible(not self.visual_splitter.isVisible())
