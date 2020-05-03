import copy
import json
import logging

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
from module.properties.u16_property import U16Property
from module.properties.u8_property import U8Property


class PropertyContainer:
    def __init__(self):
        super().__init__()
        self._properties = {}
        self.self_reference_properties = []
        self.display_property_name = None
        self.fallback_display_property_name = None
        self.id_property_name = None
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
            "buffer": BufferProperty,
            "fe13_growths": FE13GrowthsProperty,
            "u8": U8Property,
            "i8": I8Property,
            "u16": U16Property,
            "i16": I16Property,
            "i32": I32Property,
            "f32": F32Property
        }

        con = PropertyContainer()
        for key in js:
            logging.debug("Parsing property %s" % key)
            property_config = js[key]
            property_type = properties[property_config["type"]]
            prop = property_type.from_json(key, property_config)
            con[prop.name] = prop
            if type(prop) is SelfReferencePointerProperty:
                con.self_reference_properties.append(prop.name)
            if prop.is_display:
                con.display_property_name = prop.name
            if prop.is_fallback_display:
                con.fallback_display_property_name = prop.name
            if prop.is_id:
                con.id_property_name = prop.name
        return con

    def duplicate(self, new_owner=None) -> "PropertyContainer":
        result = copy.deepcopy(self)
        for prop in result.values():
            prop.parent = result
        result.owner = new_owner
        return result

    def copy_to(self, other: "PropertyContainer"):
        # Copy properties.
        for (key, value) in other.items():
            if not value.is_id:
                self._properties[key].copy_to(value)

        # Run post-copy operations.
        if self.owner and hasattr(self.owner, "extension"):
            self.owner.extension.on_copy(self.owner, self, other)

    def __setitem__(self, key: str, value: AbstractProperty):
        self._properties[key] = value

    def __getitem__(self, name: str):
        return self._properties[name]

    def values(self):
        return self._properties.values()

    def keys(self):
        return self._properties.keys()

    def items(self):
        return self._properties.items()
