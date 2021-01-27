from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (
    QListView,
    QAbstractItemView,
    QComboBox,
    QDialogButtonBox,
    QFormLayout,
    QVBoxLayout,
    QDialog,
)


class Ui_AdvancedCopyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.list = QListView()
        self.list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.combo_box = QComboBox()

        self.form_layout = QFormLayout()
        self.form_layout.addRow("Fields", self.list)
        self.form_layout.addRow("Destination", self.combo_box)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addWidget(self.buttons)
        self.setLayout(self.main_layout)

        self.setWindowTitle("Paragon - Advanced Copy")
        self.setWindowIcon(QIcon("paragon.ico"))
        self.setModal(True)
