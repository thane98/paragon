from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QDialog
from ui.autogen.ui_error_dialog import Ui_error_dialog


class ErrorDialog(QDialog, Ui_error_dialog):
    def __init__(self, error_message):
        super().__init__()
        self.setupUi(self)
        self.error_label.setText(error_message)
        self.setWindowIcon(QIcon("paragon.ico"))
