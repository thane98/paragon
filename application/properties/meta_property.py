from utils.checked_json import read_key_optional
from .abstract_property import AbstractProperty


class MetaProperty(AbstractProperty):
    def __init__(self, name, value=None):
        super().__init__(name)
        self.value = value

    def copy_to(self, destination):
        destination[self.name].value = self.value

    @classmethod
    def from_json(cls, name, json):
        result = MetaProperty(name)
        result.value = read_key_optional(json, "value", None)
        return result

    def read(self, reader):
        pass

    def write(self, writer):
        pass

    def create_editor(self):
        return None
