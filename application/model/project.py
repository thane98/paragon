import logging
import os
import fefeditor2
from enum import Enum


class Game(Enum):
    FE13 = 0
    FE14 = 1
    FE15 = 2


class Project:
    def __init__(self, rom_path: str, patch_path: str, game: int, language: int):
        logging.info("Creating project.")

        if not os.path.isdir(rom_path) or not os.path.isdir(patch_path):
            logging.error("Invalid rom or patch directory. Aborting project creation.")
            raise NotADirectoryError
        if game not in range(0, 3) or language not in range(0, 7):
            logging.error("Invalid game or language. Aborting project creation")
            raise IndexError

        self.game = game
        self.language = language
        self.rom_path = rom_path
        self.patch_path = patch_path

        if game == Game.FE13.value:
            self.filesystem = fefeditor2.create_fe13_file_system(rom_path, patch_path, language)
        elif game == Game.FE14.value:
            self.filesystem = fefeditor2.create_fe14_file_system(rom_path, patch_path, language)
        elif game == Game.FE15.value:
            self.filesystem = fefeditor2.create_fe15_file_system(rom_path, patch_path, language)
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
        return Project(rom_path, patch_path, game, language)

    def to_dict(self):
        return {
            "rom_path": self.rom_path,
            "patch_path": self.patch_path,
            "game": self.game,
            "language": self.language
        }
