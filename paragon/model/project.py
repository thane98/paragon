from pydantic import BaseModel
from paragon.model.game import Game
from paragon.model.language import Language


class Project(BaseModel):
    name: str
    rom_path: str
    output_path: str
    language: Language
    game: Game

    def get_id(self):
        return self.name + self.rom_path + self.output_path + self.game.name
