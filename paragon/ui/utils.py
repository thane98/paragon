import traceback
from typing import Optional

from PySide6.QtCore import QMimeData
from PySide6.QtGui import QIcon, QClipboard
from PySide6.QtWidgets import QMessageBox
from paragon.ui.controllers.error_dialog import ErrorDialog


def capitalize(field_id, name):
    if name:
        return name
    else:
        return " ".join(map(lambda s: s.capitalize(), field_id.split("_")))


def error(window):
    window.error_dialog = ErrorDialog(traceback.format_exc())
    window.error_dialog.show()


def warning(text, title):
    message_box = QMessageBox()
    message_box.setText(text)
    message_box.setWindowTitle(title)
    message_box.setWindowIcon(QIcon("paragon.ico"))
    message_box.setIcon(QMessageBox.Warning)
    message_box.exec_()


def info(text, title):
    message_box = QMessageBox()
    message_box.setText(text)
    message_box.setWindowTitle(title)
    message_box.setWindowIcon(QIcon("paragon.ico"))
    message_box.setIcon(QMessageBox.Information)
    message_box.exec_()


def put_rid_on_clipboard(rid):
    raw_rid = rid.to_bytes(8, "little")
    mime_data = QMimeData()
    mime_data.setData("application/paragon-rid", raw_rid)
    clipboard = QClipboard()
    clipboard.setMimeData(mime_data)


def get_rid_from_clipboard() -> Optional[int]:
    clipboard = QClipboard()
    mime_data = clipboard.mimeData()
    if not mime_data.hasFormat("application/paragon-rid"):
        return None
    data = mime_data.data("application/paragon-rid")
    return int.from_bytes(data, "little", signed=False)
