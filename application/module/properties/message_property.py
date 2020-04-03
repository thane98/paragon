from PySide2.QtWidgets import QWidget

from module.properties.abstract_property import AbstractProperty
from services import service_locator
from ui.widgets.message_property_editor import MessagePropertyEditor
from utils.checked_json import read_key_optional


class MessageProperty(AbstractProperty):
    def __init__(self, name, target_message_archive):
        super().__init__(name)
        self.key = None
        self.value = None
        self.archive = None
        self.archive_path = target_message_archive

    # Defer opening the archive until read/write to avoid "zombie" archives if module parsing fails.
    def _open_archive(self):
        open_files_service = service_locator.locator.get_scoped("OpenFilesService")
        self.archive = open_files_service.open_message_archive(self.archive_path)

    def copy_to(self, destination):
        destination[self.name].archive = self.archive
        destination[self.name].key = self.key
        destination[self.name].value = self.value

    def update_key(self, new_key):
        self.key = new_key
        if self.archive.has_message(self.key):
            self.value = self.archive.get_message(self.key)
        else:
            self.value = ""

    def update_value(self, new_value):
        self.value = new_value
        self.archive.insert_or_overwrite_message(self.key, self.value)

    @classmethod
    def from_json(cls, name, json):
        target_message_archive = json["file"]
        result = MessageProperty(name, target_message_archive)
        result.is_display = read_key_optional(json, "display", False)
        result.is_fallback_display = read_key_optional(json, "fallback_display", False)
        return result

    def read(self, reader):
        self._open_archive()
        self.key = reader.read_string()
        if self.archive.has_message(self.key):
            self.value = self.archive.get_message(self.key)
        else:
            self.value = ""

    def write(self, writer):
        self._open_archive()
        writer.write_string(self.key)
        if self.value:
            self.archive.insert_or_overwrite_message(self.key, self.value)

    def create_editor(self) -> QWidget:
        return MessagePropertyEditor(self.name)
