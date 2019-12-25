from copy import deepcopy
from PySide2.QtWidgets import QWidget
from services import service_locator
from .abstract_property import AbstractProperty
from ui.widgets.reference_property_editor import ReferencePropertyEditor


class ReferenceProperty(AbstractProperty):
    def __init__(self, name, target_module, target_property):
        super().__init__(name)
        self.target_module = target_module
        self.target_property = target_property
        self.value = None

    def _get_target_module(self):
        driver = service_locator.locator.get_scoped("Driver")
        return driver.modules[self.target_module]

    def copy_to(self, destination):
        destination[self.name].value = self.value

    @classmethod
    def from_json(cls, name, json):
        target_module = json["target_module"]
        target_property = json["target_property"]
        return ReferenceProperty(name, target_module, target_property)

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
