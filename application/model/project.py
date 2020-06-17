import logging
import os
import fefeditor2
from enum import Enum


class Game(Enum):
    FE13 = 0
    FE14 = 1
    FE15 = 2


_LANGUAGE_NUM_TO_NAME = [
    "English (NA)",
    "English (EU)",
    "Japanese",
    "French",
    "Spanish",
    "German",
    "Italian"
]


class Project:
    def __init__(self, rom_path: str, patch_path: str, game: int, language: int, export_selections=None, metadata=None):
        logging.info("Creating project.")
        if not os.path.isdir(rom_path) or not os.path.isdir(patch_path):
            logging.error("Invalid rom or patch directory. Aborting.")
            raise NotADirectoryError
        if game not in range(0, 3) or language not in range(0, 7):
            logging.error("Invalid game or language. Aborting.")
            raise IndexError
        self.game = game
        self.language = language
        self.rom_path = rom_path
        self.patch_path = patch_path
        self.export_selections = export_selections
        self.metadata = {}

        if self.game == Game.FE13.value:
            self.filesystem = fefeditor2.create_fe13_file_system(self.rom_path, self.patch_path, self.language)
        elif self.game == Game.FE14.value:
            self.filesystem = fefeditor2.create_fe14_file_system(self.rom_path, self.patch_path, self.language)
        elif self.game == Game.FE15.value:
            self.filesystem = fefeditor2.create_fe15_file_system(self.rom_path, self.patch_path, self.language)
        else:
            logging.error("Unrecognized game. Aborting project creation.")
            raise NotImplementedError

    @classmethod
    def from_json(cls, js):
        logging.info("Loading project from json.")

        game = js["game"]
        language = js["language"]
        rom_path = js["rom_path"]
        patch_path = js["patch_path"]
        export_selections = js.get("export_selections")
        metadata = js.get("metadata", {})
        return Project(rom_path, patch_path, game, language, export_selections, metadata)

    def to_dict(self):
        return {
            "rom_path": self.rom_path,
            "patch_path": self.patch_path,
            "game": self.game,
            "language": self.language,
            "export_selections": self.export_selections,
            "metadata": self.metadata
        }

    def get_language_name(self):
        return _LANGUAGE_NUM_TO_NAME[self.language]

    def get_game_name(self):
        return Game(self.game).name

    def get_module_dir(self):
        if self.game == Game.FE13.value:
            return "Modules/FE13/"
        elif self.game == Game.FE14.value:
            return "Modules/FE14/"
        else:
            return "Modules/FE15/"
