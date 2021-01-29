import logging
from typing import Optional

from PySide2 import QtCore
from PySide2.QtCore import QSortFilterProxyModel, QModelIndex, QPoint
from PySide2.QtGui import QPixmap, QKeySequence
from PySide2.QtWidgets import QGraphicsScene, QInputDialog, QMenu, QShortcut, QWidget, QHBoxLayout, QScrollArea

from module.properties.property_container import PropertyContainer
from module.table_module import TableModule
from services.service_locator import locator
from ui.property_form import PropertyForm
from ui.views.ui_fe14_character_editor import Ui_FE14CharacterEditor
from ui.fe14.fe14_conversation_editor import FE14ConversationEditor
from ui.widgets.dialogue_editor import DialogueEditor
from ui.widgets.fe14_supports_widget import FE14SupportWidget
from ui.widgets.merged_flags_editor import MergedFlagsEditor
from ui.widgets.merged_stats_editor import MergedStatsEditor


class FE14CharacterEditor(Ui_FE14CharacterEditor):
    def __init__(self, is_person=False, parent=None):
        super().__init__(parent)
        self.is_person = is_person
        self.module: TableModule = locator.get_scoped("ModuleService").get_module("Characters")
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.proxy_model.setSourceModel(self.module.entries_model)
        self.characters_list_view.setModel(self.proxy_model)
        self.selection: Optional[PropertyContainer] = None

        self.character_details_form_1 = PropertyForm(self.module.element_template, category="character_description_1")
        self.character_details_form_contents_1.setLayout(self.character_details_form_1)
        self.character_details_form_2 = PropertyForm(self.module.element_template, category="character_description_2")
        self.character_details_form_contents_2.setLayout(self.character_details_form_2)
        self.character_details_form_2.fix_editor_width(100)
        self.stats_editor = MergedStatsEditor(["Bases", "Growths", "Modifiers", "Penalties", "Bonuses"])
        self.stats_form = PropertyForm(self.module.element_template, category="stats")
        self.stats_layout.addWidget(self.stats_editor)
        self.stats_layout.addLayout(self.stats_form)
        self.skills_form = PropertyForm(self.module.element_template, category="skills", sort_editors=True)
        self.skills_contents.setLayout(self.skills_form)
        self.flags_editor = MergedFlagsEditor(
            ["Bitflags (1)", "Bitflags (2)", "Bitflags (3)", "Bitflags (4)"],
            self.module.element_template
        )
        self.flags_editor_2 = MergedFlagsEditor(
            ["Bitflags (5)", "Bitflags (6)", "Bitflags (7)", "Bitflags (8)"],
            self.module.element_template
        )
        self.misc_form = PropertyForm(self.module.element_template, category="misc")
        self.misc_layout.addWidget(self.flags_editor)
        self.misc_layout.addWidget(self.flags_editor_2)
        self.misc_layout.addLayout(self.misc_form)
        self.ids_form = PropertyForm(self.module.element_template, category="ids")
        self.ids_tab.setLayout(self.ids_form)
        self.classes_form = PropertyForm(self.module.element_template, category="classes", sort_editors=True)
        self.classes_tab.setLayout(self.classes_form)
        if not self.is_person:
            self.dialogue_tab = DialogueEditor()
            self.supports_tab = QWidget()
            self.supports_layout = QHBoxLayout()
            self.supports_widget = FE14SupportWidget()
            self.supports_scroll = QScrollArea()
            self.supports_scroll_contents = QWidget()
            self.supports_scroll.setWidget(self.supports_scroll_contents)
            self.supports_scroll.setWidgetResizable(True)
            self.supports_layout.addWidget(self.supports_widget)
            self.supports_layout.addWidget(self.supports_scroll)
            self.supports_tab.setLayout(self.supports_layout)
            self.supports_form = PropertyForm(self.module.element_template, category="supports")
            self.supports_scroll_contents.setLayout(self.supports_form)
            self.tab_widget.addTab(self.supports_tab, "Supports")
            self.tab_widget.addTab(self.dialogue_tab, "Dialogue")

        self.context_menu = QMenu(self)
        self.context_menu.addActions([self.action_add, self.action_remove, self.action_copy_to])
        self.clear_selection_shortcut = QShortcut(QKeySequence.Cancel, self)

        self._install_signals()
        self._clear()

    def set_module(self, module: TableModule):
        self.module = module
        if self.module:
            self.proxy_model.setSourceModel(self.module.entries_model)
        else:
            self.proxy_model.setSourceModel(None)
        self.setEnabled(self.module is not None)
        self._clear()

    def _on_context_menu_requested(self, point: QPoint):
        self.context_menu.exec_(self.characters_list_view.mapToGlobal(point))

    def _install_signals(self):
        self.characters_list_view.selectionModel().currentRowChanged.connect(self._update_selection)
        self.characters_list_view.customContextMenuRequested.connect(self._on_context_menu_requested)
        self.search_bar.textChanged.connect(self._update_filter)
        self.action_add.triggered.connect(self._on_add_character_triggered)
        self.action_remove.triggered.connect(self._on_remove_character_triggered)
        self.action_copy_to.triggered.connect(self._on_copy_to_triggered)
        self.clear_selection_shortcut.activated.connect(self._clear)
        if self.character_details_form_1.editors['Name'] != None:
            self.character_details_form_1.editors['Name'].value_editor.editingFinished.connect(self._update_conversation_widget)

    def _clear(self):
        self.characters_list_view.clearSelection()
        self.characters_list_view.selectionModel().clearCurrentIndex()

    def _update_selection(self, index: QModelIndex):
        self.selection = self.proxy_model.data(index, QtCore.Qt.UserRole)
        self.portraits_tab.update_target(self.selection)
        self.character_details_form_1.update_target(self.selection)
        self.character_details_form_2.update_target(self.selection)
        self.stats_editor.update_target(self.selection)
        self.ids_form.update_target(self.selection)
        self.classes_form.update_target(self.selection)
        self.stats_form.update_target(self.selection)
        self.skills_form.update_target(self.selection)
        self.flags_editor.update_target(self.selection)
        self.flags_editor_2.update_target(self.selection)
        self.misc_form.update_target(self.selection)
        if not self.is_person:
            self.dialogue_tab.update_target(self.selection)
            self.supports_widget.update_target(self.selection)
            self.supports_form.update_target(self.selection)
        if self.selection:
            locator.get_scoped("SpriteService").get_sprite_for_character(self.selection, 0)
        self.action_remove.setEnabled(self.selection is not None)
        self.action_copy_to.setEnabled(self.selection is not None)
        self._update_portrait_box()

    def _update_portrait_box(self):
        portrait_service = locator.get_scoped("PortraitService")
        mini_portraits = portrait_service.get_sorted_portraits_for_character(self.selection, "bu")
        if mini_portraits:
            _, texture = mini_portraits[0]
            scene = QGraphicsScene()
            scene.addPixmap(QPixmap.fromImage(texture.image()))
            self.portrait_display.setScene(scene)
        else:
            self.portrait_display.setScene(None)

    def _update_filter(self):
        self.proxy_model.setFilterRegExp(self.search_bar.text())

    def _on_add_character_triggered(self):
        model = self.module.entries_model
        model.insertRow(model.rowCount())
        source = self.module.entries[0]
        destination = self.module.entries[-1]
        source.copy_to(destination)
        # Update any present conversation widget with the new obj list
        self._update_conversation_widget()

    def _on_remove_character_triggered(self):
        if self.characters_list_view.currentIndex().isValid():
            model = self.module.entries_model
            model.removeRow(self.characters_list_view.currentIndex().row())
            model.beginResetModel()
            model.endResetModel()
            # Update any present conversation widget with the new obj list
            self._update_conversation_widget()

    def _update_conversation_widget(self):        
        for editor in self.supports_widget.service._conversation_editors:
            editor: FE14ConversationEditor
            character_list = list()
            [character_list.append(child[1]) for child in self.module.children()]
            editor.text_area._character_list = character_list

    def _on_copy_to_triggered(self):
        if not self.selection:
            return

        logging.info("Beginning copy to for " + self.module.name)
        choices = []
        for i in range(0, len(self.module.entries)):
            choices.append(str(i + 1) + ". " + self.module.entries[i].get_display_name())
        choice = QInputDialog.getItem(self, "Select Destination", "Destination", choices)
        if choice[1]:
            for i in range(0, len(choices)):
                if choice[0] == choices[i]:
                    self.selection.copy_to(self.module.entries[i])
            # Update any present conversation widget with the new obj list
            self._update_conversation_widget()
        else:
            logging.info("No choice selected for " + self.module.name + " copy to. Aborting.")