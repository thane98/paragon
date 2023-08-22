from PySide2.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListView, QHBoxLayout


class Ui_CmpWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.file_list = QListView()
        self.new_file_button = QPushButton("Insert")
        self.delete_file_button = QPushButton("Delete")
        self.extract_file_button = QPushButton("Extract")
        self.replace_file_button = QPushButton("Replace")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.new_file_button)
        button_layout.addWidget(self.delete_file_button)
        button_layout.addWidget(self.extract_file_button)
        button_layout.addWidget(self.replace_file_button)
        layout = QVBoxLayout()
        layout.addWidget(self.file_list)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setContentsMargins(0, 0, 0, 0)
