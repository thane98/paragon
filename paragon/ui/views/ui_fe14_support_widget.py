from PySide2.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QListView, QAbstractItemView


class Ui_FE14SupportWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.supports_list = QListView()
        self.supports_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.supports_list.setDragEnabled(True)
        self.supports_list.setDropIndicatorShown(True)
        self.supports_list.setAcceptDrops(True)

        self.new_button = QPushButton("New")
        self.delete_button = QPushButton("Delete")
        self.open_button = QPushButton("Open Dialogue")

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.new_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.open_button)

        layout = QVBoxLayout()
        layout.addWidget(self.supports_list)
        layout.addLayout(buttons_layout)

        main_layout = QHBoxLayout()
        main_layout.addLayout(layout)

        self.setLayout(main_layout)
