from PySide6 import QtCore
from PySide6.QtCore import QSortFilterProxyModel
from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QWidget, QPushButton

from paragon.core.services.fe15_dungeons import FE15Dungeons
from paragon.model.fe15_dungeon_info import FE15DungeonInfo
from paragon.ui.auto_widget_generator import AutoWidgetGenerator
from paragon.ui.controllers.map_editor import MapEditor
from paragon.ui.views.ui_fe15_dungeon_editor import Ui_FE15DungeonEditor


class FE15DungeonEditor(Ui_FE15DungeonEditor):
    def __init__(self, gs, ms):
        super().__init__()

        self.gd = gs.data
        self.gs = gs
        self.ms = ms
        self.dungeon_service: FE15Dungeons = gs.dungeons

        generator = AutoWidgetGenerator(ms, gs)
        self.field_widget = generator.generate_for_type("Field")
        self.encount_field_widget = generator.generate_for_type("Field")
        self.map_editor = MapEditor(ms, gs)
        self.tabs.addTab(self._build_encount_config_tab(generator), "Encounter Config")
        self.tabs.addTab(self.encount_field_widget, "Encounter Field")
        self.tabs.addTab(self.map_editor, "Encounter Map")
        self.tabs.addTab(self.field_widget, "Dungeon Field")
        self.tabs.addTab(self._build_drops_tab(generator), "Drops")

        self.drop_group_list = self.drop_group_widget.gen_widgets[
            "dungeon_drop_group_data_table"
        ]
        self.encount_field_line_edit = self.field_widget.gen_widgets[
            "encounter_field_line_edit"
        ]
        self.encount_terrain_line_edit = self.encount_field_widget.gen_widgets[
            "encounter_terrain_line_edit"
        ]
        self.encount_dispos_line_edit = self.encount_field_widget.gen_widgets[
            "encounter_dispos_line_edit"
        ]

        model = self.dungeon_service.get_dungeons_model()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(model)
        self.list.setModel(self.proxy_model)

        self.list.selectionModel().currentChanged.connect(
            self._on_select, QtCore.Qt.UniqueConnection
        )
        self.drop_group_list.item_selected.connect(
            lambda rid: self.drop_list_widget.set_target(
                self.dungeon_service.get_drop_list_from_drop_group(rid)
            )
        )
        self.toggle_dungeon_list_action.triggered.connect(
            self._on_toggle_dungeon_list, QtCore.Qt.UniqueConnection
        )
        self.search.textChanged.connect(self._on_search, QtCore.Qt.UniqueConnection)
        self.refresh_factions_button.clicked.connect(self._on_refresh_map_factions)

    def _on_search(self):
        self.proxy_model.setFilterRegularExpression(self.search.text())

    def _on_toggle_dungeon_list(self):
        self.left_widget.setVisible(not self.left_widget.isVisible())

    def _build_encount_config_tab(self, generator: AutoWidgetGenerator):
        self.encount_widget = generator.generate_for_type("EncounterTable")
        self.refresh_factions_button = QPushButton("Refresh Map Factions")
        self.refresh_factions_button.setEnabled(False)

        refresh_factions_group_box = QGroupBox("Actions")
        refresh_factions_layout = QVBoxLayout()
        refresh_factions_layout.addWidget(self.refresh_factions_button)
        refresh_factions_group_box.setLayout(refresh_factions_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(refresh_factions_group_box)
        main_layout.addWidget(self.encount_widget)

        wrapper = QWidget()
        wrapper.setContentsMargins(0, 0, 0, 0)
        wrapper.setLayout(main_layout)
        return wrapper

    def _build_drops_tab(self, generator: AutoWidgetGenerator):
        self.drop_group_widget = generator.generate_for_type(
            "DungeonDropGroupDataTable"
        )
        self.drop_list_widget = generator.generate_for_type("DungeonDropListDataTable")

        drop_group_box = QGroupBox("Drop Group")
        drop_group_box.setContentsMargins(0, 0, 0, 0)
        drop_group_layout = QVBoxLayout()
        drop_group_layout.addWidget(self.drop_group_widget)
        drop_group_box.setLayout(drop_group_layout)

        drop_list_box = QGroupBox("Drop List")
        drop_list_box.setContentsMargins(0, 0, 0, 0)
        drop_list_layout = QVBoxLayout()
        drop_list_layout.addWidget(self.drop_list_widget)
        drop_list_box.setLayout(drop_list_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(drop_group_box)
        main_layout.addWidget(drop_list_box)
        main_layout.setStretch(1, 1)

        wrapper = QWidget()
        wrapper.setContentsMargins(0, 0, 0, 0)
        wrapper.setLayout(main_layout)
        return wrapper

    def _on_refresh_map_factions(self):
        selection = self.list.model().data(self.list.currentIndex(), QtCore.Qt.UserRole)
        if selection:
            dungeon_info = self.dungeon_service.load_dungeon(selection)
            if dungeon_info and dungeon_info.dispos:
                self.map_editor.restrict_factions(
                    self.dungeon_service.get_encounter_factions(dungeon_info)
                )

    def _on_select(self):
        selection = self.list.model().data(self.list.currentIndex(), QtCore.Qt.UserRole)
        if not selection:
            self._clear()
        else:
            dungeon_info = self.dungeon_service.load_dungeon(selection)
            if dungeon_info:
                self.dungeon_service.mark_dirty(dungeon_info)
                self._load_dungeon_info(dungeon_info)
            else:
                self._clear()

    def _load_dungeon_info(self, dungeon_info: FE15DungeonInfo):
        self.drop_group_widget.set_target(dungeon_info.drop_group)
        self.field_widget.set_target(dungeon_info.dungeon_field)
        self.encount_widget.set_target(dungeon_info.encount)
        self.encount_field_widget.set_target(dungeon_info.encount_field)
        self.map_editor.set_target(
            None,
            dungeon_info.terrain_key,
            None,
            dungeon_info.dispos,
            dungeon_info.terrain,
        )
        self.map_editor.restrict_factions(
            self.dungeon_service.get_encounter_factions(dungeon_info)
        )

        self.encount_field_line_edit.setEnabled(False)
        self.encount_terrain_line_edit.setEnabled(False)
        self.encount_dispos_line_edit.setEnabled(False)
        self.refresh_factions_button.setEnabled(dungeon_info.dispos is not None)

    def _clear(self):
        self.drop_group_widget.set_target(None)
        self.field_widget.set_target(None)
        self.encount_widget.set_target(None)
        self.encount_field_widget.set_target(None)
        self.map.set_target(None, None, None, None, None)
        self.refresh_factions_button.setEnabled(False)
