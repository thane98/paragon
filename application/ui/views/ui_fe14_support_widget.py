from PySide2 import QtGui
from PySide2.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout, QComboBox, QFormLayout


class Ui_FE14SupportWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.characters_widget = QListWidget()
        self.supports_widget = QListWidget()
        self.add_button = QPushButton(text="Add")
        self.remove_button = QPushButton(text="Remove")
        self.add_remove_layout = QHBoxLayout()
        self.add_remove_layout.addWidget(self.add_button)
        self.add_remove_layout.addWidget(self.remove_button)
        self.add_remove_layout.setAlignment(QtGui.Qt.AlignCenter)

        self.selection_layout = QVBoxLayout()
        self.selection_layout.addWidget(self.characters_widget)
        self.selection_layout.addLayout(self.add_remove_layout)
        self.selection_layout.addWidget(self.supports_widget)

        self.support_type_box = QComboBox()
        self.support_type_box.addItems(["Romantic", "Platonic", "Fast Romantic", "Fast Platonic"])
        self.support_form_layout = QFormLayout()
        self.support_form_layout.addRow("Type", self.support_type_box)
        self.selection_layout.addLayout(self.support_form_layout)

        self.setLayout(self.selection_layout)
