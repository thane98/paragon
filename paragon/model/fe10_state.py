import dataclasses

from paragon.core.services.dialogue import Dialogue
from paragon.core.services.portraits import Portraits

from paragon.core.services.icons import Icons

from paragon.core.services.write_preprocessors import WritePreprocessors

from paragon.ui.specs import Specs

from paragon.ui.models import Models

from paragon.ui.enum_loader import EnumLoader

from paragon.model.project import Project
from paragon import paragon as paragon_core


@dataclasses.dataclass
class FE10State:
    project: Project
    data: paragon_core.GameData
    specs: Specs
    models: Models
    enums: EnumLoader
    icons: Icons
    portraits: Portraits
    dialogue: Dialogue
    write_preprocessors: WritePreprocessors
