from copy import deepcopy
from typing import Any

from PySide2.QtWidgets import QWidget
from services.service_locator import locator
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
        destination.value = self.value

    @classmethod
    def _from_json(cls, name, json):
        target_module = json["target_module"]
        target_property = json["target_property"]
        result = ReferenceProperty(name, target_module, target_property)
        result.is_display = json.get("display", False)
        result.is_fallback_display = json.get("fallback_display", False)
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

    def export(self) -> Any:
        module = self._get_target_module()
        element = module.get_element_by_property_and_value(self.target_property, self.value)
        if element:
            return element.get_key()
        else:
            return None

    def import_values(self, values_json: Any):
        module = self._get_target_module()
        element = module.get_element_by_key(values_json)
        return element[self.target_property].value
