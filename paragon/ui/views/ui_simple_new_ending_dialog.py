from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QComboBox,
    QLineEdit,
    QFormLayout,
    QDialogButtonBox,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
)


class Ui_SimpleNewEndingDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.char1_box = QComboBox()
        self.char2_box = QComboBox()

        form_layout = QFormLayout()
        form_layout.addRow("Character 1", self.char1_box)
        form_layout.addRow("Character 2", self.char2_box)

        self.completion_graphic = QLabel()
        self.info_label = QLabel()

        info_layout = QHBoxLayout()
        info_layout.addWidget(self.completion_graphic)
        info_layout.addWidget(self.info_label)
        info_layout.setStretch(1, 1)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(info_layout)
        main_layout.addWidget(self.buttons)
        self.setLayout(main_layout)

        self.setModal(True)
        self.setFixedSize(450, 160)
        self.setWindowTitle("New Ending")
        self.setWindowIcon(QIcon("paragon.ico"))
