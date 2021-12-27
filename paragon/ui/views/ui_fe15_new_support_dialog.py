from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (
    QDialog,
    QComboBox,
    QLineEdit,
    QFormLayout,
    QDialogButtonBox,
    QVBoxLayout,
    QLabel,
    QStyle,
    QHBoxLayout,
    QCheckBox,
)

from paragon.model.support_info import DialogueType
from paragon.ui.controllers.enum_combo_box import EnumComboBox


class Ui_FE15NewSupportDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.character = QComboBox()
        self.character.setStyleSheet("combobox-popup: 0;")
        self.conditions_check_box = QCheckBox("Unlock Conditions")
        self.conditions_check_box.setChecked(True)
        self.dialogue_check_box = QCheckBox("Dialogue")
        self.dialogue_check_box.setChecked(True)

        self.completion_graphic = QLabel()
        self.user_info = QLabel()

        info_layout = QHBoxLayout()
        info_layout.addWidget(self.completion_graphic)
        info_layout.addWidget(self.user_info)
        info_layout.setStretch(1, 1)

        form_layout = QFormLayout()
        form_layout.addRow("Character", self.character)
        form_layout.addRow(self.conditions_check_box)
        form_layout.addRow(self.dialogue_check_box)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        style = self.style()
        ok = self.buttons.button(QDialogButtonBox.Ok)
        cancel = self.buttons.button(QDialogButtonBox.Cancel)
        ok.setIcon(style.standardIcon(QStyle.SP_DialogOkButton))
        cancel.setIcon(style.standardIcon(QStyle.SP_DialogCancelButton))

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(info_layout)
        main_layout.addWidget(self.buttons)
        self.setLayout(main_layout)

        self.setModal(True)
        self.setFixedSize(500, 200)
        self.setWindowTitle("New Support")
        self.setWindowIcon(QIcon("paragon.ico"))
