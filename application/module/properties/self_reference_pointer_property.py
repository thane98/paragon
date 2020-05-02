from typing import Optional

from PySide2.QtWidgets import QWidget

from services.service_locator import locator
from ui.widgets.reference_property_editor import ReferencePropertyEditor
from ui.widgets.self_reference_pointer_property_editor import SelfReferencePointerPropertyEditor
from .abstract_property import AbstractProperty


class SelfReferencePointerProperty(AbstractProperty):
    def __init__(self, name, target_module):
        super().__init__(name)
        self.target_module = target_module
        self.value = None
        self.target_element_address: Optional[int] = None

    def _get_target_module(self):
        module_service = locator.get_scoped("ModuleService")
        return module_service.get_module(self.target_module)

    def copy_to(self, destination):
        destination.value = self.value

    @classmethod
    def _from_json(cls, name, json):
        target_module = json["target_module"]
        result = SelfReferencePointerProperty(name, target_module)
        return result

    def read(self, reader):
        # We don't have enough information to get the value yet.
        # Need to read all entries first.
        self.target_element_address = reader.read_internal_pointer()

    def write(self, writer):
        if not self.value:
            writer.write_u32(0)
        else:
            module = self._get_target_module()
            base_address = module.find_base_address_for_element(self.value)
            writer.write_pointer(base_address)

    def create_editor(self) -> QWidget:
        return SelfReferencePointerPropertyEditor(self.name, self._get_target_module())
