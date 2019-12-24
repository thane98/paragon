from PySide2.QtWidgets import QWidget
from properties.abstract_property import AbstractProperty
from ui.widgets.message_property_editor import MessagePropertyEditor
from utils.checked_json import read_key_optional


class MessageProperty(AbstractProperty):
    def __init__(self, name, target_message_archive, driver):
        super().__init__(name)
        self.key = None
        self.value = None
        self.driver = driver
        self.archive = None
        self.archive_path = target_message_archive

    def __deepcopy__(self, memo):
        result = MessageProperty(self.name, self.archive_path, self.driver)
        result.key = self.key
        result.value = self.value
        result.archive = self.archive
        memo[id(self)] = result
        return result

    # Defer opening the archive until read/write to avoid "zombie" archives if module parsing fails.
    def _open_archive(self):
        open_files_service = self.driver.open_files_service
        self.archive = open_files_service.open_message_archive(self.archive_path)

    def copy_to(self, destination):
        destination[self.name].key = self.key
        destination[self.name].value = self.value

    @classmethod
    def from_json(cls, driver, name, json):
        target_message_archive = json["file"]
        result = MessageProperty(name, target_message_archive, driver)
        result.is_display = read_key_optional(json, "display", False)
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
