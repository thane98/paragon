import copy
import json
import logging
from typing import List, Optional, Dict, Tuple

from core.export_capabilities import ExportCapabilities, ExportCapability
from module.properties.abstract_property import AbstractProperty
from module.properties.buffer_property import BufferProperty
from module.properties.f32_property import F32Property
from module.properties.fe13_growths_property import FE13GrowthsProperty
from module.properties.i16_property import I16Property
from module.properties.i32_property import I32Property
from module.properties.i8_property import I8Property
from module.properties.mapped_property import MappedProperty
from module.properties.message_property import MessageProperty
from module.properties.reference_property import ReferenceProperty
from module.properties.self_reference_pointer_property import SelfReferencePointerProperty
from module.properties.string_property import StringProperty
from module.properties.suffix_property import SuffixProperty
from module.properties.u16_property import U16Property
from module.properties.u32_property import U32Property
from module.properties.u8_property import U8Property


class PropertyContainer:
    def __init__(self):
        super().__init__()
        self._properties = {}
        self.self_reference_properties = []
        self.pointer_properties = []
        self.display_property_name = None
        self.fallback_display_property_name = None
        self.id_property_name = None
        self.key_property_name = None
        self.owner = None

    @staticmethod
    def from_file(file_path: str):
        with open(file_path, "r") as f:
            js = json.load(f)
            return PropertyContainer.from_json(js)

    @staticmethod
    def from_json(js):
        from module.properties.pointer_property import PointerProperty
        properties = {
            "pointer": PointerProperty,
            "self_reference": SelfReferencePointerProperty,
            "mapped": MappedProperty,
            "message": MessageProperty,
            "reference": ReferenceProperty,
            "string": StringProperty,
            "suffix": SuffixProperty,
            "buffer": BufferProperty,
            "fe13_growths": FE13GrowthsProperty,
            "u8": U8Property,
            "i8": I8Property,
            "u16": U16Property,
            "i16": I16Property,
            "i32": I32Property,
            "u32": U32Property,
            "f32": F32Property
        }

        con = PropertyContainer()
        for key in js:
            logging.debug("Parsing property %s" % key)
            property_config = js[key]
            property_type = properties[property_config["type"]]
            prop = property_type.from_json(key, property_config)
            con[prop.name] = prop
            if prop.is_display:
                con.display_property_name = prop.name
            if prop.is_fallback_display:
                con.fallback_display_property_name = prop.name
            if prop.is_id:
                con.id_property_name = prop.name
            if prop.is_key:
                con.key_property_name = prop.name
        return con

    def get_display_name(self) -> str:
        if self.display_property_name:
            result = self._properties[self.display_property_name].value
            if result:
                return result
        if self.fallback_display_property_name:
            result = self._properties[self.fallback_display_property_name].value
            if result:
                return result
        return "Element " + str(self.owner.index_of(self))

    def get_key(self) -> str:
        if not self.key_property_name:
            return str(self.owner.index_of(self))
        return self._properties[self.key_property_name].value

    def set_key(self, key: str):
        if not self.key_property_name:
            raise NotImplementedError("Cannot set a key for a container which has no key properties.")
        self._properties[self.key_property_name] = key

    def has_key_property(self) -> bool:
        return self.key_property_name is not None

    def duplicate(self, new_owner=None) -> "PropertyContainer":
        result = copy.deepcopy(self)
        for prop in result.values():
            prop.parent = result
        result.owner = new_owner
        return result

    def export(self, properties: Optional[List[str]] = None) -> Dict:
        if properties:
            properties_to_export = properties
        else:
            properties_to_export = self._properties.keys()

        data_to_export = {}
        for property_key in properties_to_export:
            if property_key not in self._properties:
                raise KeyError("Attempted to export the non-existent property %s." % property_key)
            else:
                data_to_export[property_key] = self._properties[property_key].export()
        return data_to_export

    def import_values(self, values):
        for property_key in values:
            if property_key == "__CREATE_NEW__":
                continue
            if property_key not in self._properties:
                raise KeyError("Cannot import values into non-existent property %s." % property_key)
            self._properties[property_key].import_values(values[property_key])

    def children(self) -> List[Tuple[AbstractProperty, str, str]]:
        return [(prop, prop.name, prop.name) for prop in self._properties.values() if prop.exportable]

    @staticmethod
    def export_capabilities() -> ExportCapabilities:
        capabilities = [
            ExportCapability.Selectable,
            ExportCapability.Appendable
        ]
        return ExportCapabilities(capabilities)

    def copy_to(self, other: "PropertyContainer"):
        # Copy properties.
        for (key, value) in other.items():
            if not value.is_id:
                self._properties[key].copy_to(value)

        # Run post-copy operations.
        if self.owner and hasattr(self.owner, "extension"):
            print(self.owner.extension)
            self.owner.extension.on_copy(self.owner, self, other)

    def __setitem__(self, key: str, value: AbstractProperty):
        from module.properties.pointer_property import PointerProperty
        if type(value) is SelfReferencePointerProperty and key not in self.self_reference_properties:
            self.self_reference_properties.append(key)
        elif type(value) is PointerProperty and key not in self.pointer_properties:
            self.pointer_properties.append(key)
        self._properties[key] = value

    def __getitem__(self, name: str):
        return self._properties[name]

    def values(self):
        return self._properties.values()

    def keys(self):
        return self._properties.keys()

    def items(self):
        return self._properties.items()
