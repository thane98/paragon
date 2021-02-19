from typing import Optional

from PySide2.QtWidgets import QTabWidget, QGridLayout, QWidget
from paragon.model.chapter_data import ChapterData

from paragon.model.game import Game

from paragon.ui.controllers.dialogue_editor import DialogueEditor

from paragon.ui.auto_widget_generator import AutoWidgetGenerator
from paragon.ui.controllers.map_editor import MapEditor


class FE13ChapterEditorTabs(QTabWidget):
    def __init__(self, ms, gs):
        super().__init__()
        self.gd = gs.data
        self.chapters = gs.chapters

        gen = AutoWidgetGenerator(ms, gs)
        self.chapter = gen.generate_for_type("Chapter")
        self.config = gen.generate_for_type("MapConfig")
        self.person = gen.generate_for_type("PersonFile")
        self.landscape = gen.generate_for_type("Landscape")
        self.dialogue = DialogueEditor(gs.data, gs.dialogue, Game.FE13)
        self.map = MapEditor(ms, gs)

        grid = QGridLayout()
        grid.addWidget(self.chapter, 0, 0, 2, 1)
        grid.addWidget(self.config, 0, 1)
        grid_widget = QWidget()
        grid_widget.setLayout(grid)

        self.addTab(grid_widget, "Overview")
        self.addTab(self.map, "Map")
        self.addTab(self.person, "Chapter Characters")
        self.addTab(self.landscape, "Landscape")
        self.addTab(self.dialogue, "Dialogue")

    def set_target(self, data: Optional[ChapterData]):
        if data:
            self.chapter.set_target(data.decl)
            self.config.set_target(data.config)
            self.person.set_target(data.person)
            self.landscape.set_target(data.landscape)
            self.dialogue.set_archive(data.dialogue, True)
            self.map.set_target(data.cid, data.person_key, data.dispos, data.terrain)
        else:
            self.chapter.set_target(None)
            self.config.set_target(None)
            self.person.set_target(None)
            self.landscape.set_target(None)
            self.dialogue.set_archive(None, False)
            self.map.set_target(None, None, None, None)
