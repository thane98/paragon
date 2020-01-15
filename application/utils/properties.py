from properties.buffer_property import BufferProperty
from properties.f32_property import F32Property
from properties.i16_property import I16Property
from properties.i32_property import I32Property
from properties.i8_property import I8Property
from properties.mapped_property import MappedProperty
from properties.message_property import MessageProperty
from properties.reference_property import ReferenceProperty
from properties.string_property import StringProperty
from properties.u16_property import U16Property
from properties.u8_property import U8Property

TRIVIAL_PROPERTIES = {
    "mapped": MappedProperty,
    "message": MessageProperty,
    "string": StringProperty,
    "buffer": BufferProperty,
    "u8": U8Property,
    "i8": I8Property,
    "u16": U16Property,
    "i16": I16Property,
    "u32": I32Property,
    "f32": F32Property,
    "reference": ReferenceProperty
}


def read_trivial_properties(json):
    result = {}
    for property_name in json:
        property_config = json[property_name]
        property_type = TRIVIAL_PROPERTIES[property_config["type"]]
        result[property_name] = (property_type.from_json(property_name, property_config))
    return result
