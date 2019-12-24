from copy import deepcopy

from PySide2.QtWidgets import QWidget

from .abstract_property import AbstractProperty
from ui.widgets.reference_property_editor import ReferencePropertyEditor


class ReferenceProperty(AbstractProperty):
    def __init__(self, name, driver, target_module, target_property):
        super().__init__(name)
        self.driver = driver
        self.target_module = target_module
        self.target_property = target_property
        self.value = None

    def __deepcopy__(self, memo):
        result = ReferenceProperty(self.name, self.driver, self.target_module, self.target_property)
        result.value = self.value
        memo[id(self)] = result
        return result

    def _get_target_module(self):
        return self.driver.modules[self.target_module]

    def copy_to(self, destination):
        destination[self.name].value = self.value

    @classmethod
    def from_json(cls, driver, name, json):
        target_module = json["target_module"]
        target_property = json["target_property"]
        return ReferenceProperty(name, driver, target_module, target_property)

    def read(self, reader):
        module = self._get_target_module()
        if module.element_template[self.target_property] is ReferenceProperty:
            raise TypeError
        target_property = deepcopy(module.element_template[self.target_property])
        target_property.read(reader)
        self.value = target_property.value

    def write(self, writer):
        module = self._get_target_module()
        if module.element_template[self.target_property] is ReferenceProperty:
            raise TypeError
        target_property = deepcopy(module.element_template[self.target_property])
        target_property.value = self.value
        target_property.write(writer)

    def create_editor(self) -> QWidget:
        return ReferencePropertyEditor(self.name, self._get_target_module(), self.target_property)
