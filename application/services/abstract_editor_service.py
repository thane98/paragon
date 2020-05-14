from abc import ABC, abstractmethod
from PySide2.QtWidgets import QWidget

from core.export_capabilities import ExportCapabilities


class AbstractEditorService(ABC):
    @abstractmethod
    def get_editor(self) -> QWidget:
        pass

    @abstractmethod
    def get_display_name(self) -> str:
        pass

    @abstractmethod
    def save(self):
        pass

    def export_capabilities(self) -> ExportCapabilities:
        return ExportCapabilities([])
