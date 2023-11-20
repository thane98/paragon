from typing import Optional

from PySide6.QtGui import QStandardItemModel, QStandardItem


class CmpFileModel(QStandardItemModel):
    def __init__(self, gd, archive: str):
        super().__init__()
        self.gd = gd
        self.archive_name = archive
        for f in gd.list_cmp_files(archive):
            self.appendRow(QStandardItem(f))

    def delete_file(self, filename: str):
        self.gd.delete_cmp_file(self.archive_name, filename)
        item = self._filename_to_item(filename)
        if item:
            self.removeRow(item.row())

    def write_file(self, filename: str, contents: bytes):
        self.gd.write_to_cmp(self.archive_name, filename, contents)
        if not self._filename_to_item(filename):
            self.appendRow(QStandardItem(filename))

    def extract_file(self, filename: str, destination_path: str):
        contents = self.gd.read_cmp_file(self.archive_name, filename)
        with open(destination_path, "wb") as f:
            f.write(bytes(contents))

    def _filename_to_item(self, filename: str) -> Optional[QStandardItem]:
        for i in range(0, self.rowCount()):
            item = self.item(i)
            if item.text() == filename:
                return item
        return None
