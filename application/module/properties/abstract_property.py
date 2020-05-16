from abc import ABC, abstractmethod
from typing import Any

from PySide2.QtWidgets import QWidget

from core.export_capabilities import ExportCapabilities, ExportCapability


class AbstractProperty(ABC):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.is_display = False
        self.is_fallback_display = False
        self.exportable = True
        self.is_id = False
        self.is_key = False
        self.linked_property = None
        self.is_disabled = False
        self.offset = -1
        self.parent = None
        self.tooltip = None

    @abstractmethod
    def copy_to(self, destination):
        pass

    @classmethod
    def from_json(cls, name, json):
        result = cls._from_json(name, json)
        result.exportable = json.get("exportable", True)
        if result.is_id:
            result.is_disabled = True
            result.exportable = False
        result.is_disabled = json.get("disabled", result.is_disabled)
        result.tooltip = json.get("tooltip", None)
        return result

    @classmethod
    @abstractmethod
    def _from_json(cls, name, json):
        raise NotImplementedError

    @abstractmethod
    def read(self, reader):
        raise NotImplementedError

    @abstractmethod
    def write(self, writer):
        raise NotImplementedError

    @abstractmethod
    def export(self) -> Any:
        pass

    @staticmethod
    def export_capabilities() -> ExportCapabilities:
        return ExportCapabilities([ExportCapability.Selectable])

    @abstractmethod
    def import_values(self, values_json: Any):
        pass

    @abstractmethod
    def create_editor(self) -> QWidget:
        raise NotImplementedError
