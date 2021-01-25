from PySide2.QtWidgets import QWidget

from ui.widgets.fe14_ai_combo_box import FE14AIComboBox
from ui.widgets.string_property_line_edit import StringPropertyLineEdit
from .plain_value_property import PlainValueProperty


class StringProperty(PlainValueProperty):
    def __init__(self, name, value=None):
        super().__init__(name)
        self.editor_factory = lambda: StringPropertyLineEdit(self.name)
        self.value = value

    def copy_to(self, destination):
        destination.value = self.value

    def set_value(self, new_value, follow_link=True):
        self.value = new_value
        if self.linked_property and follow_link:
            linked_property = self.parent[self.linked_property]
            linked_property.set_value(self.value, follow_link=False)

    @classmethod
    def _from_json(cls, name, json):
        result = StringProperty(name)
        result.is_key = json.get("key", False)
        result.is_display = json.get("display", False)
        result.is_fallback_display = json.get("fallback_display", False)
        result.linked_property = json.get("linked_property", None)
        if "editor" in json:
            result.editor_factory = cls._parse_editor(result, json["editor"])
        return result

    @staticmethod
    def _parse_editor(prop, json):
        editor_type = json["type"]
        if editor_type == "fe14_ai":
            label = json["label"]
            return lambda: FE14AIComboBox(prop.name, label)
        else:
            return lambda: StringPropertyLineEdit(prop.name)

    def read(self, reader):
        self.value = reader.read_string()

    def write(self, writer):
        writer.write_string(self.value)

    def create_editor(self) -> QWidget:
        return self.editor_factory()
