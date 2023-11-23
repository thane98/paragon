from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QComboBox,
    QLineEdit,
    QFormLayout,
    QDialogButtonBox,
    QVBoxLayout,
)


class Ui_FE14NewChapterDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.source = QComboBox()
        self.cid = QLineEdit()
        self.route = QComboBox()
        self.route.addItems(["All Routes", "Birthright", "Conquest", "Revelation"])

        form_layout = QFormLayout()
        form_layout.addRow("Template", self.source)
        form_layout.addRow("CID", self.cid)
        form_layout.addRow("Route", self.route)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.buttons)
        self.setLayout(main_layout)

        self.setModal(True)
        self.setFixedSize(450, 175)
        self.setWindowTitle("New Chapter")
        self.setWindowIcon(QIcon("paragon.ico"))
