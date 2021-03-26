from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (
    QDialog,
    QComboBox,
    QLineEdit,
    QFormLayout,
    QDialogButtonBox,
    QVBoxLayout,
)


class Ui_NewChapterDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.source = QComboBox()
        self.cid = QLineEdit()

        form_layout = QFormLayout()
        form_layout.addRow("Template", self.source)
        form_layout.addRow("CID", self.cid)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.buttons)
        self.setLayout(main_layout)

        self.setModal(True)
        self.setFixedSize(450, 125)
        self.setWindowTitle("New Chapter")
        self.setWindowIcon(QIcon("paragon.ico"))
