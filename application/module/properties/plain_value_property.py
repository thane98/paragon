from abc import ABC
from typing import Any

from module.properties.abstract_property import AbstractProperty


class PlainValueProperty(AbstractProperty, ABC):
    def __init__(self, name: str):
        super().__init__(name)
        self.value = None

    def export(self) -> Any:
        return self.value

    def import_values(self, values_json: Any):
        if values_json and self.value and not isinstance(values_json, type(self.value)):
            raise TypeError("Type mismatch when importing values into property %s." % self.name)
        else:
            self.value = values_json
