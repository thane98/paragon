import fefeditor2
from typing import List
from bin_streams import BinArchiveReader, BinArchiveWriter


class MessageArchive:
    def __init__(self):
        self.title: str = ""
        self._messages = {}
        self.dirty = False

    def insert_or_overwrite_message(self, key, value):
        if key in self._messages and self._messages[key] != value:
            self.dirty = True
        self._messages[key] = value

    def get_message(self, key):
        return self._messages[key]

    def has_message(self, key):
        return key in self._messages

    def read(self, archive):
        reader = BinArchiveReader(archive)
        self.title = reader.read_utf8_string()
        while reader.tell() < archive.size():
            key = reader.read_mapped()
            value = reader.read_utf16_string()
            self._messages[key] = value

    @staticmethod
    def _write_bytes(result, values):
        for b in values:
            result.append(b)

    def _write_utf8(self, result: List, value: str):
        utf8 = value.encode("utf8")
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
        self._write_utf8(result, self.title)
        for (key, value) in self._messages.items():
            archive.set_mapped_pointer(len(result), key)
            self._write_utf16(result, value)

        archive.allocate_at_end(len(result))
        writer = BinArchiveWriter(archive)
        writer.write_bytes(result)
        return archive
