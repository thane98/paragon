from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QGroupBox,
    QFormLayout,
    QComboBox,
    QLineEdit,
    QVBoxLayout,
)
from paragon.ui.controllers.auto.portrait_viewer import PortraitViewer


class Ui_AvatarConfigWindow(QDialog):
    def __init__(self, ms, gs):
        super().__init__()

        self.name = QLineEdit()
        self.portraits = QComboBox()
        self.portraits.setStyleSheet("combobox-popup: 0;")
        self.accessory = QComboBox()
        self.accessory.setStyleSheet("combobox-popup; 0;")
        self.gender = QComboBox()
        self.gender.addItems(["Male", "Female"])

        config_layout = QFormLayout()
        config_layout.addRow("Name", self.name)
        config_layout.addRow("Gender", self.gender)
        config_layout.addRow("Portraits", self.portraits)
        config_layout.addRow("Accessory", self.accessory)

        config_box = QGroupBox("Config")
        config_box.setLayout(config_layout)

        self.preview = PortraitViewer.new(ms, gs, retrieve_mode="face_data")

        layout = QVBoxLayout()
        layout.addWidget(config_box)
        layout.addWidget(self.preview)
        self.setLayout(layout)

        self.setModal(True)
        self.setWindowTitle("Configure Avatar")
        self.setWindowIcon(QIcon("paragon.ico"))
