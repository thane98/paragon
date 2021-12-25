from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QGroupBox, QTabWidget, QLabel, QVBoxLayout


class Ui_FE14FieldEditor(QWidget):
    def __init__(self):
        super().__init__()

        self.info_box = QGroupBox("Info.")
        self.info_label = QLabel(
            "This editor can be used to change where/what 3D models get placed on the map."
        )
        info_layout = QVBoxLayout()
        info_layout.addWidget(self.info_label)
        self.info_box.setLayout(info_layout)

        self.tabs = QTabWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.info_box)
        layout.addWidget(self.tabs)
        self.setLayout(layout)

        self.setWindowIcon(QIcon("paragon.ico"))
        self.resize(800, 600)
