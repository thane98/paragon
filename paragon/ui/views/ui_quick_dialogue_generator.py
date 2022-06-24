from PySide2.QtGui import QIcon, QFont
from PySide2.QtWidgets import (
    QWidget,
    QComboBox,
    QPlainTextEdit,
    QFormLayout,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QCheckBox,
    QSpinBox,
    QFormLayout,
)


class Ui_QuickDialogueGenerator(QWidget):
    def __init__(self):
        super().__init__()

        self.character1_box = QComboBox()
        self.character1_box.setStyleSheet("combobox-popup: 0;")
        self.character1_form = QFormLayout()
        self.character1_form.addRow("Character 1", self.character1_box)

        self.character2_box = QComboBox()
        self.character2_box.setStyleSheet("combobox-popup: 0;")
        self.character2_form = QFormLayout()
        self.character2_form.addRow("Character 2", self.character2_box)

        self.inputs_layout = QHBoxLayout()
        self.inputs_layout.addLayout(self.character1_form)
        self.inputs_layout.addLayout(self.character2_form)

        editor_font = QFont()
        editor_font.setPointSize(11)  # TODO: Make this configurable

        self.dialogue_editor = QPlainTextEdit()
        self.dialogue_editor.setFont(editor_font)
        self.dialogue_editor.setPlaceholderText(
            "Enter dialogue of the form:\n\nFelicia: Hello!\nMozu: Goodbye."
        )

        result_layout = QVBoxLayout()
        result_layout.setContentsMargins(0, 0, 0, 0)
        self.result_display = QPlainTextEdit()
        self.result_display.setFont(editor_font)
        self.result_display.setPlaceholderText("Converted dialogue will appear here.")
        self.result_display.setReadOnly(True)
        self.copy_button = QPushButton("Copy Text")
        result_layout.addWidget(self.result_display)
        result_layout.addWidget(self.copy_button)

        self.dialogue_layout = QHBoxLayout()
        self.dialogue_layout.addWidget(self.dialogue_editor)
        self.dialogue_layout.addLayout(result_layout)

        self.auto_line_break_check_box = QCheckBox("Auto Line Break")

        self.line_break_width_spin_box = QSpinBox()
        self.line_break_width_spin_box.setRange(10, 100)
        self.line_break_width_spin_box.setValue(30)
        config_form = QFormLayout()
        config_form.addRow("Line Break Width", self.line_break_width_spin_box)

        self.convert_button = QPushButton("Convert to Paragon Script")

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.inputs_layout)
        self.main_layout.addLayout(self.dialogue_layout)
        self.main_layout.addWidget(self.auto_line_break_check_box)
        self.main_layout.addLayout(config_form)
        self.main_layout.addWidget(self.convert_button)

        self.setLayout(self.main_layout)
        self.resize(1000, 700)
        self.setWindowTitle("Paragon")
        self.setWindowIcon(QIcon("paragon.ico"))
