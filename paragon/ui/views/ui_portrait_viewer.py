from PySide2 import QtGui
from PySide2.QtWidgets import (
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QWidget,
    QComboBox,
)
from paragon.ui.controllers.image_graphics_view import ImageGraphicsView

class Ui_PortraitViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.show_buttons_layout = QHBoxLayout()
        self.show_buttons_layout.setAlignment(QtGui.Qt.AlignCenter)
        self.mode_combo_box = QComboBox()

        self.display = ImageGraphicsView()
        self.display.setMinimumSize(256, 300)

        self.portrait_name_label = QLabel(text="(None)")
        self.portrait_name_label.setAlignment(QtGui.Qt.AlignCenter)

        self.navigation_buttons_layout = QHBoxLayout()
        self.navigation_buttons_layout.setAlignment(QtGui.Qt.AlignCenter)
        self.back_button = QPushButton("<")
        self.current_image_label = QLabel(text="0 / 0")
        self.forward_button = QPushButton(">")
        self.navigation_buttons_layout.addWidget(self.back_button)
        self.navigation_buttons_layout.addWidget(self.current_image_label)
        self.navigation_buttons_layout.addWidget(self.forward_button)

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(QtGui.Qt.AlignCenter)
        self.main_layout.addWidget(self.mode_combo_box)
        self.main_layout.addWidget(self.display)
        self.main_layout.addWidget(self.portrait_name_label)
        self.main_layout.addLayout(self.navigation_buttons_layout)
        self.setLayout(self.main_layout)
