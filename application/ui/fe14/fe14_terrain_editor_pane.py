from typing import Optional

from PySide2.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QPushButton

from model.fe14.terrain import Terrain, get_tile_template
from module.properties.property_container import PropertyContainer
from ui.property_form import PropertyForm


class FE14TerrainEditorPane(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        terrain = Terrain()
        persistent_properties_template = terrain.adapter()
        self.persistent_scroll, self.persistent_form = PropertyForm.create_with_scroll(persistent_properties_template)
        self.tile_scroll, self.tile_form = PropertyForm.create_with_scroll(get_tile_template())
        self.toggle_persistent_button = QPushButton(text="Toggle Map/Grid Properties")
        self.persistent_scroll.setFixedHeight(300)

        self.layout = QVBoxLayout()
        self.container = QWidget()
        self.layout.addWidget(self.toggle_persistent_button)
        self.layout.addWidget(self.persistent_scroll)
        self.layout.addWidget(self.tile_scroll)
        self.container.setLayout(self.layout)
        self.setWidgetResizable(True)
        self.setWidget(self.container)

        self.toggle_persistent_button.clicked.connect(self._on_toggle_persistent_button_pressed)

    def _on_toggle_persistent_button_pressed(self):
        self.persistent_scroll.setVisible(not self.persistent_scroll.isVisible())

    def update_chapter_data(self, chapter_data):
        if chapter_data and chapter_data.terrain:
            self.persistent_form.update_target(chapter_data.terrain.adapter())
        else:
            self.persistent_form.update_target(None)
        self.setEnabled(chapter_data is not None and chapter_data.terrain is not None)
        self.tile_form.update_target(None)

    def update_tile_target(self, new_target: Optional[PropertyContainer]):
        self.tile_form.update_target(new_target)
