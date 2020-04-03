import logging

from module.properties.abstract_property import AbstractProperty
from module.properties.buffer_property import BufferProperty
from module.properties.f32_property import F32Property
from module.properties.i16_property import I16Property
from module.properties.i32_property import I32Property
from module.properties.i8_property import I8Property
from module.properties.mapped_property import MappedProperty
from module.properties.message_property import MessageProperty
from module.properties.reference_property import ReferenceProperty
from module.properties.string_property import StringProperty
from module.properties.u16_property import U16Property
from module.properties.u8_property import U8Property


class PropertyContainer:
    def __init__(self):
        super().__init__()
        self._properties = {}
        self.display_property_name = None
        self.fallback_display_property_name = None
        self.table_key = None

    @staticmethod
    def from_json(js):
        from module.properties.pointer_property import PointerProperty
        properties = {
            "pointer": PointerProperty,
            "mapped": MappedProperty,
            "message": MessageProperty,
            "reference": ReferenceProperty,
            "string": StringProperty,
            "buffer": BufferProperty,
            "u8": U8Property,
            "i8": I8Property,
            "u16": U16Property,
            "i16": I16Property,
            "i32": I32Property,
            "f32": F32Property
        }

        con = PropertyContainer()
        for key in js:
            logging.info("Parsing property %s" % key)
            property_config = js[key]
            property_type = properties[property_config["type"]]
            prop = property_type.from_json(key, property_config)
            con[prop.name] = prop
            if prop.is_display:
                con.display_property_name = prop.name
            if prop.is_fallback_display:
                con.fallback_display_property_name = prop.name
        return con

    def copy_to(self, other: "PropertyContainer"):
        for (key, value) in other._properties:
            self._properties[key].copy_to(value)

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
