import dataclasses

from paragon.core.services.chapters import Chapters
from paragon.core.services.endings import Endings
from paragon.core.services.fe13_supports import FE13Supports

from paragon.core.services.sprites import Sprites
from paragon.core.services.sprite_animation import SpriteAnimation

from paragon.core.services.dialogue import Dialogue
from paragon.core.services.icons import Icons
from paragon.core.services.portraits import Portraits
from paragon.core.services.write_preprocessors import WritePreprocessors
from paragon.model.project import Project
from paragon import paragon as paragon_core
from paragon.ui.enum_loader import EnumLoader
from paragon.ui.models import Models
from paragon.ui.specs import Specs


@dataclasses.dataclass
class FE13State:
    project: Project
    data: paragon_core.GameData
    specs: Specs
    models: Models
    enums: EnumLoader
    icons: Icons
    portraits: Portraits
    dialogue: Dialogue
    sprites: Sprites
    supports: FE13Supports
    sprite_animation: SpriteAnimation
    chapters: Chapters
    endings: Endings
    write_preprocessors: WritePreprocessors
