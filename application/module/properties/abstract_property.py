from abc import ABC, abstractmethod
from PySide2.QtWidgets import QWidget


class AbstractProperty(ABC):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.is_display = False
        self.is_fallback_display = False
        self.offset = -1

    @abstractmethod
    def copy_to(self, destination):
        pass

    @classmethod
    @abstractmethod
    def from_json(cls, name, json):
        raise NotImplementedError

    @abstractmethod
    def read(self, reader):
        raise NotImplementedError

    @abstractmethod
    def write(self, writer):
        raise NotImplementedError

    @abstractmethod
    def create_editor(self) -> QWidget:
        raise NotImplementedError
