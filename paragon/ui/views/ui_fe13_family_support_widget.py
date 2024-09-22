from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QListWidget,
    QStyle,
)


class Ui_FE13FamilySupportWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.supports_list = QListWidget()

        self.new_button = QPushButton("New")
        self.open_button = QPushButton("Open Dialogue")

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.new_button)
        buttons_layout.addWidget(self.open_button)

        layout = QVBoxLayout()
        layout.addWidget(self.supports_list)
        layout.addLayout(buttons_layout)

        main_layout = QHBoxLayout()
        main_layout.addLayout(layout)

        self.setLayout(main_layout)
