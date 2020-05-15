from enum import Enum
from typing import List


class ExportCapability(Enum):
    Selectable = 0,
    Appendable = 1


class ExportCapabilities:
    def __init__(self, capabilities: List[ExportCapability]):
        self._is_selectable = ExportCapability.Selectable in capabilities
        self._is_appendable = ExportCapability.Appendable in capabilities

    def is_selectable(self) -> bool:
        return self._is_selectable

    def is_appendable(self) -> bool:
        return self._is_appendable
