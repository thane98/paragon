from PySide6.QtWidgets import QWidget, QPushButton, QSizePolicy, QLabel, QHBoxLayout


class Ui_ColorPicker(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.color_label = QLabel()
        self.color_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.color_label.setFixedSize(50, 50)
        self.color_button = QPushButton("Change Color")
        layout.addWidget(self.color_label)
        layout.addWidget(self.color_button)
        layout.addStretch()
        self.setLayout(layout)
