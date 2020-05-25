import fefeditor2
from typing import List
from core.bin_streams import BinArchiveWriter, BinArchiveReader


class MessageArchive:
    def __init__(self):
        self.title: str = ""
        self._messages = {}
        self.dirty = False
        self.localized = True

    def messages(self):
        return self._messages.items()

    def insert_or_overwrite_message(self, key, value):
        value_to_write = value.replace("\\n", '\n')
        if key not in self._messages or (key in self._messages and self._messages[key] != value_to_write):
            self.dirty = True
        self._messages[key] = value_to_write

    def get_message(self, key):
        return self._messages[key].replace('\n', "\\n")

    def has_message(self, key):
        return key in self._messages

    def read(self, archive):
        reader = BinArchiveReader(archive)
        self.title = reader.read_shift_jis_string()
        while reader.tell() < archive.size():
            key = reader.read_mapped()
            value = reader.read_utf16_string()
            self._messages[key] = value

    @staticmethod
    def _write_bytes(result, values):
        for b in values:
            result.append(b)

    def _write_shift_jis(self, result: List, value: str):
        utf8 = value.encode("shift-jis")
        self._write_bytes(result, utf8)
        result.append(0)
        while len(result) % 4 != 0:
            result.append(0)

    def _write_utf16(self, result: List, value):
        utf16 = value.encode("UTF-16LE")
        self._write_bytes(result, utf16)
        self._write_bytes(result, [0, 0])
        while len(result) % 4 != 0:
            result.append(0)

    def to_bin(self):
        archive = fefeditor2.create_bin_archive()
        result = []
        self._write_shift_jis(result, self.title)
        for (key, value) in self._messages.items():
            archive.set_mapped_pointer(len(result), key)
            self._write_utf16(result, value)

        archive.allocate_at_end(len(result))
        writer = BinArchiveWriter(archive)
        writer.write_bytes(result)
        return archive
