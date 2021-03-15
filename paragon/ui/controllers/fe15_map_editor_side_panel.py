from PySide2.QtWidgets import QWidget, QScrollArea, QVBoxLayout
from paragon.ui.auto_widget_generator import AutoWidgetGenerator


class FE15MapEditorSidePanel(QWidget):
    def __init__(self, ms, gs):
        super().__init__()

        gen = AutoWidgetGenerator(ms, gs)
        self.spawn_ui = gen.generate_for_type("Spawn")
        self.grid_ui = gen.generate_for_type("Grid")
        self.tile_ui = gen.generate_for_type("Tile")

        self.terrain_ui = QScrollArea()
        terrain_widget = QWidget()
        terrain_layout = QVBoxLayout()
        terrain_layout.addWidget(self.grid_ui)
        terrain_layout.addWidget(self.tile_ui)
        terrain_layout.setStretch(1, 1)
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
        self.grid_ui.set_target(terrain)

    def set_tile_target(self, tile, **kwargs):
        self.tile_ui.set_target(tile)

    def set_spawn_target(self, spawn):
        self.spawn_ui.set_target(spawn)

    def get_spawn_widgets(self):
        return self.spawn_ui.gen_widgets
