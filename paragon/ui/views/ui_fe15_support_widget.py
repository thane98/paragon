from PySide6.QtWidgets import (
    QWidget,
    QListView,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QGroupBox,
    QSplitter,
    QScrollArea,
)


class Ui_FE15SupportWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setContentsMargins(0, 0, 0, 0)

        self.supports_list = QListView()

        self.new_button = QPushButton("New")
        self.delete_button = QPushButton("Delete")

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.new_button)
        buttons_layout.addWidget(self.delete_button)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.supports_list)
        layout.addLayout(buttons_layout)

        side_bar_wrapper = QWidget()
        side_bar_wrapper.setContentsMargins(0, 0, 0, 0)
        side_bar_wrapper.setLayout(layout)

        self.add_conditions_button = QPushButton("Add Unlock Conditions")
        self.add_dialogue_button = QPushButton("Add Dialogue")
        self.open_button = QPushButton("Open Dialogue")

        actions_layout = QHBoxLayout()
        actions_layout.addWidget(self.add_conditions_button)
        actions_layout.addWidget(self.add_dialogue_button)
        actions_layout.addWidget(self.open_button)

        self.actions_box = QGroupBox("Actions")
        self.actions_box.setLayout(actions_layout)

        self.conditions_box = QGroupBox("Unlock Conditions")
        conditions_wrapper = QVBoxLayout()
        self.conditions_box.setLayout(conditions_wrapper)

        self.content_layout = QVBoxLayout()
        self.content_layout.addWidget(self.actions_box)
        self.content_layout.addWidget(self.conditions_box)

        content_wrapper = QWidget()
        content_wrapper.setLayout(self.content_layout)

        content_scroll = QScrollArea()
        content_scroll.setWidgetResizable(True)
        content_scroll.setWidget(content_wrapper)

        splitter = QSplitter()
        splitter.setContentsMargins(0, 0, 0, 0)
        splitter.addWidget(side_bar_wrapper)
        splitter.addWidget(content_scroll)
        splitter.setStretchFactor(1, 1)

        splitter_wrapper = QVBoxLayout()
        splitter_wrapper.addWidget(splitter)

        self.setLayout(splitter_wrapper)
