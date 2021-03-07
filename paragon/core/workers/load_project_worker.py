import logging
import os
import traceback

from PySide2.QtCore import QObject, Signal
from paragon.model.configuration import Configuration

from paragon import paragon as pgn
from paragon.core.services.fe13_chapters import FE13Chapters
from paragon.core.services.fe13_dialogue import FE13Dialogue
from paragon.core.services.fe13_icons import FE13Icons
from paragon.core.services.fe13_portraits import FE13Portraits
from paragon.core.services.fe13_sprites import FE13Sprites
from paragon.core.services.fe14_chapters import FE14Chapters
from paragon.core.services.fe14_dialogue import FE14Dialogue
from paragon.core.services.fe14_icons import FE14Icons
from paragon.core.services.fe14_portraits import FE14Portraits
from paragon.core.services.fe14_sprites import FE14Sprites
from paragon.core.services.fe14_supports import FE14Supports
from paragon.core.services.fe14_write_preprocessors import FE14WritePreprocessors
from paragon.core.services.fe15_dialogue import FE15Dialogue
from paragon.core.services.fe15_icons import FE15Icons
from paragon.core.services.fe15_portraits import FE15Portraits
from paragon.core.services.fe15_sprites import FE15Sprites
from paragon.core.services.sprite_animation import SpriteAnimation
from paragon.core.services.write_preprocessors import WritePreprocessors
from paragon.model.fe13_state import FE13State
from paragon.model.fe14_state import FE14State
from paragon.model.fe15_state import FE15State
from paragon.model.game import Game
from paragon.model.project import Project
from paragon.ui.enum_loader import EnumLoader
from paragon.ui.models import Models
from paragon.ui.specs import Specs


# TODO: Make this multithreaded again.
class LoadProjectWorker(QObject):
    succeeded = Signal(object)
    error = Signal(tuple)

    def __init__(self, config: Configuration, project: Project):
        QObject.__init__(self)
        self.project = project
        self.config = config

    def run(self):
        config_root = os.path.join(os.getcwd(), "Data", self.project.game.value)
        try:
            logging.debug(
                f"Loading {self.project.output_path}, {self.project.rom_path}, {config_root}"
            )
            gd = pgn.GameData.load(
                self.project.output_path,
                self.project.rom_path,
                self.project.game.value,
                self.project.language.value,
                config_root,
            )
            gd.read()

            specs = Specs.load(os.path.join(config_root, "UI", "Modules"))
            enums = EnumLoader(os.path.join(config_root, "UI", "Enums"))

            if self.project.game == Game.FE13:
                icons = FE13Icons(gd)
                models = Models(gd, icons)
                portraits = FE13Portraits(self.config, gd)
                sprites = FE13Sprites(gd)
                state = FE13State(
                    project=self.project,
                    data=gd,
                    specs=specs,
                    enums=enums,
                    models=models,
                    icons=icons,
                    portraits=portraits,
                    dialogue=FE13Dialogue(self.config, gd, portraits, config_root),
                    sprites=sprites,
                    sprite_animation=SpriteAnimation(),
                    chapters=FE13Chapters(gd, models, icons),
                    write_preprocessors=WritePreprocessors(),
                )
            elif self.project.game == Game.FE14:
                icons = FE14Icons(gd)
                models = Models(gd, icons)
                portraits = FE14Portraits(self.config, gd)
                dialogue = FE14Dialogue(self.config, gd, portraits, config_root)
                sprites = FE14Sprites(gd)
                chapters = FE14Chapters(gd, models, icons)
                state = FE14State(
                    project=self.project,
                    data=gd,
                    specs=specs,
                    enums=enums,
                    models=models,
                    icons=icons,
                    write_preprocessors=FE14WritePreprocessors(),
                    portraits=portraits,
                    dialogue=dialogue,
                    sprites=sprites,
                    sprite_animation=SpriteAnimation(),
                    chapters=chapters,
                    supports=FE14Supports(gd),
                )
            elif self.project.game == Game.FE15:
                icons = FE15Icons(gd)
                models = Models(gd, icons)
                portraits = FE15Portraits(self.config, gd)
                sprites = FE15Sprites(gd)
                state = FE15State(
                    project=self.project,
                    data=gd,
                    specs=specs,
                    enums=enums,
                    models=models,
                    icons=icons,
                    portraits=portraits,
                    dialogue=FE15Dialogue(self.config, gd, portraits, config_root),
                    sprites=sprites,
                    sprite_animation=SpriteAnimation(),
                    write_preprocessors=WritePreprocessors(),
                )
            else:
                raise NotImplementedError("Unsupported game.")
            self.succeeded.emit(state)
        except Exception as e:
            logging.exception("Load project failed.")
            trace = traceback.format_exc()
            self.error.emit((trace, e))
