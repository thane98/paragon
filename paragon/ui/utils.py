import traceback

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMessageBox
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
