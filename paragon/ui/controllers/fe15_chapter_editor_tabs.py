from typing import Optional

from PySide6.QtWidgets import QTabWidget, QGridLayout, QWidget
from paragon.model.chapter_data import ChapterData

from paragon.model.game import Game

from paragon.ui.controllers.dialogue_editor import DialogueEditor

from paragon.ui.auto_widget_generator import AutoWidgetGenerator
from paragon.ui.controllers.map_editor import MapEditor


class FE15ChapterEditorTabs(QTabWidget):
    def __init__(self, ms, gs):
        super().__init__()
        self.gd = gs.data
        self.chapters = gs.chapters

        gen = AutoWidgetGenerator(ms, gs)
        self.chapter_events = gen.generate_for_type("EventDeclGrouping")
        self.chapter = gen.generate_for_type("Chapter")
        self.dialogue = DialogueEditor(
            gs.data, gs.dialogue, gs.sprite_animation, Game.FE15
        )
        self.map = MapEditor(ms, gs)

        self.addTab(self.chapter, "Overview")
        self.addTab(self.map, "Map")
        self.addTab(self.chapter_events, "Event")
        self.addTab(self.dialogue, "Dialogue")

    def set_target(self, data: Optional[ChapterData]):
        if data:
            self.chapter.set_target(data.decl)
            self.chapter_events.set_target(data.event)
            self.dialogue.set_archive(data.dialogue, True)
            self.map.set_target(
                data.cid, data.terrain_key, data.person_key, data.dispos, data.terrain
            )
        else:
            self.chapter.set_target(None)
            self.chapter_events.set_target(None)
            self.dialogue.set_archive(None, False)
            self.map.set_target(None, None, None, None, None)
