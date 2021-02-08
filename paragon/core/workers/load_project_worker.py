import logging
import os
import traceback

from PySide2.QtCore import QObject, Signal, QRunnable, Slot
from paragon.core.services.fe13_sprites import FE13Sprites

from paragon.core.services.fe13_dialogue import FE13Dialogue
from paragon.core.services.fe13_portraits import FE13Portraits
from paragon.core.services.fe15_dialogue import FE15Dialogue

from paragon.core.services.fe15_portraits import FE15Portraits

from paragon.core.services.fe13_icons import FE13Icons
from paragon.core.services.fe14_icons import FE14Icons
from paragon.core.services.fe15_icons import FE15Icons

from paragon import paragon as pgn
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

    def __init__(self, project: Project):
        QObject.__init__(self)
        self.project = project

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
                portraits = FE13Portraits(gd)
                sprites = FE13Sprites(gd)
                state = FE13State(
                    project=self.project,
                    data=gd,
                    specs=specs,
                    enums=enums,
                    models=models,
                    icons=icons,
                    portraits=portraits,
                    dialogue=FE13Dialogue(gd, portraits, config_root),
                    sprites=FE13Sprites(gd),
                )
            elif self.project.game == Game.FE14:
                icons = FE14Icons(gd)
                models = Models(gd, icons)
                state = FE14State(
                    project=self.project,
                    data=gd,
                    specs=specs,
                    enums=enums,
                    models=models,
                    icons=icons,
                )
            elif self.project.game == Game.FE15:
                icons = FE15Icons(gd)
                models = Models(gd, icons)
                portraits = FE15Portraits(gd)
                state = FE15State(
                    project=self.project,
                    data=gd,
                    specs=specs,
                    enums=enums,
                    models=models,
                    icons=icons,
                    portraits=portraits,
                    dialogue=FE15Dialogue(gd, portraits, config_root),
                )
            else:
                raise NotImplementedError("Unsupported game.")
            self.succeeded.emit(state)
        except Exception as e:
            logging.exception("Load project failed.")
            trace = traceback.format_exc()
            self.error.emit((trace, e))
