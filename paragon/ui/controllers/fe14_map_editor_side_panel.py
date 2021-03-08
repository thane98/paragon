from PySide2.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QGroupBox
from paragon.ui.controllers.auto.string_line_edit import StringLineEdit

from paragon.model.auto_generator_state import AutoGeneratorState

from paragon.ui.auto_widget_generator import AutoWidgetGenerator


class FE14MapEditorSidePanel(QWidget):
    def __init__(self, ms, gs):
        super().__init__()

        self.gd = gs.data
        gen = AutoWidgetGenerator(ms, gs)
        dummy_state = AutoGeneratorState(
            main_state=ms,
            game_state=gs,
            generator=gen,
            type_metadata={},
            field_metadata={},
            typename="Unused",
        )
        self.spawn_ui = gen.generate_for_type("Spawn")
        self.map_model_ui = StringLineEdit(dummy_state, "map_model")
        self.grid_ui = gen.generate_for_type("Grid")
        self.tile_ui = gen.generate_for_type("Tile", multi_wrap_ids=["change_id_1", "change_id_2", "change_id_3"])

        map_model_box = QGroupBox("Map Model")
        map_model_layout = QVBoxLayout()
        map_model_layout.addWidget(self.map_model_ui)
        map_model_box.setLayout(map_model_layout)

        self.terrain_ui = QScrollArea()
        terrain_widget = QWidget()
        terrain_layout = QVBoxLayout()
        terrain_layout.addWidget(self.map_model_ui)
        terrain_layout.addWidget(self.grid_ui)
        terrain_layout.addWidget(self.tile_ui)
        terrain_layout.setStretch(2, 1)
        terrain_widget.setLayout(terrain_layout)
        self.terrain_ui.setWidgetResizable(True)
        self.terrain_ui.setWidget(terrain_widget)
        self.terrain_ui.setVisible(False)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.spawn_ui)
        layout.addWidget(self.terrain_ui)
        self.setLayout(layout)

    def toggle_mode(self):
        if self.terrain_ui.isVisible():
            self.terrain_ui.setVisible(False)
            self.spawn_ui.setVisible(True)
        else:
            self.terrain_ui.setVisible(True)
            self.spawn_ui.setVisible(False)

    def clear_forms(self):
        self.set_terrain_target(None)
        self.set_tile_target(None)
        self.set_spawn_target(None)

    def set_terrain_target(self, terrain):
        self.map_model_ui.set_target(terrain)
        if not terrain:
            self.grid_ui.set_target(None)
        elif grid := self.gd.rid(terrain, "grid"):
            self.grid_ui.set_target(grid)
        else:
            self.grid_ui.set_target(None)

    def set_tile_target(self, tile, **kwargs):
        self.tile_ui.set_target(tile, multi_id="terrain", multi_key=kwargs.get("multi_key"))

    def set_spawn_target(self, spawn):
        self.spawn_ui.set_target(spawn)

    def get_spawn_widgets(self):
        return self.spawn_ui.gen_widgets
