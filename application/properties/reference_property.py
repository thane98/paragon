from copy import deepcopy
from PySide2.QtWidgets import QWidget
from services.service_locator import locator
from utils.checked_json import read_key_optional
from .abstract_property import AbstractProperty
from ui.widgets.reference_property_editor import ReferencePropertyEditor


class ReferenceProperty(AbstractProperty):
    def __init__(self, name, target_module, target_property):
        super().__init__(name)
        self.target_module = target_module
        self.target_property = target_property
        self.value = None

    def _get_target_module(self):
        module_service = locator.get_scoped("ModuleService")
        return module_service.get_module(self.target_module)

    def copy_to(self, destination):
        destination[self.name].value = self.value

    @classmethod
    def from_json(cls, name, json):
        target_module = json["target_module"]
        target_property = json["target_property"]
        result = ReferenceProperty(name, target_module, target_property)
        result.is_display = read_key_optional(json, "display", False)
        result.is_fallback_display = read_key_optional(json, "fallback_display", False)
        return result

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
