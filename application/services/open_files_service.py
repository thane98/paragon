from typing import Dict
from model.message_archive import MessageArchive


class OpenFile:
    def __init__(self, file):
        self.file = file
        self.dirty = False


class OpenFilesService:
    def __init__(self, filesystem):
        self.open_files: Dict[str: OpenFile] = {}
        self.open_message_archives: Dict[MessageArchive] = {}
        self.filesystem = filesystem

    def set_archive_in_use(self, archive):
        for entry in self.open_files.values():
            if entry.file is archive:
                entry.dirty = True
                break

    def is_archive_in_use(self, archive) -> bool:
        for entry in self.open_files.values():
            if entry.file is archive:
                return entry.dirty
        return False

    def to_valid_path_in_filesystem(self, file_path: str):
        source_path = self.filesystem.get_source_path()
        dest_path = self.filesystem.get_dest_path()
        if file_path.startswith(dest_path):
            return file_path[len(dest_path):]
        if file_path.startswith(source_path):
            return file_path[len(source_path):]
        return None

    def open(self, path_in_rom):
        if path_in_rom in self.open_files:
            return self.open_files[path_in_rom].file

        archive = self.filesystem.open_bin("/" + path_in_rom)
        self.open_files[path_in_rom] = OpenFile(archive)
        return archive

    def open_message_archive(self, path_in_rom):
        if path_in_rom in self.open_message_archives:
            return self.open_message_archives[path_in_rom]

        archive = self.filesystem.open_localized_bin("/" + path_in_rom)
        message_archive = MessageArchive()
        message_archive.read(archive)
        self.open_message_archives[path_in_rom] = message_archive
        return message_archive

    def save(self):
        for (path, open_file) in self.open_files.items():
            if open_file.dirty:
                self.filesystem.write_bin("/" + path, open_file.file)
        for (path, message_archive) in self.open_message_archives.items():
            if message_archive.dirty:
                archive = message_archive.to_bin()
                self.filesystem.write_localized_bin("/" + path, archive)

    def clear(self):
        self.open_files.clear()
