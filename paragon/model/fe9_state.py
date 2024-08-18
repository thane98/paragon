import dataclasses

from paragon.core.services.dialogue import Dialogue
from paragon.core.services.fe9_maps import FE9Maps
from paragon.core.services.gcn_sprites import GcnSprites
from paragon.core.services.portraits import Portraits

from paragon.core.services.icons import Icons
from paragon.core.services.sprite_animation import SpriteAnimation
from paragon.core.services.sprites import Sprites

from paragon.core.services.write_preprocessors import WritePreprocessors

from paragon.ui.specs import Specs

from paragon.ui.models import Models

from paragon.ui.enum_loader import EnumLoader

from paragon.model.project import Project
from paragon import paragon as paragon_core


@dataclasses.dataclass
class FE9State:
    project: Project
    data: paragon_core.GameData
    specs: Specs
    models: Models
    enums: EnumLoader
    icons: Icons
    portraits: Portraits
    dialogue: Dialogue
    maps: FE9Maps
    sprites: GcnSprites
    sprite_animation: SpriteAnimation
    write_preprocessors: WritePreprocessors
