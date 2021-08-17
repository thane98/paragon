from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QListWidget, QVBoxLayout, QSplitter, QToolBar, \
    QPushButton, QPlainTextEdit, QComboBox


class Ui_LayeredDirEditor(QSplitter):
    def __init__(self, has_sub_entries):
        super().__init__()

        self.list_widget = QListWidget()

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.list_widget)
        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        self.save_button = QPushButton("Save")
        self.tool_bar = QToolBar()
        self.tool_bar.addWidget(self.save_button)
        self.editor = QPlainTextEdit()

        self.entries_box = QComboBox()
        self.entries_box.setMinimumWidth(300)
        if has_sub_entries:
            self.tool_bar.addSeparator()
            self.tool_bar.addWidget(self.entries_box)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.tool_bar)
        right_layout.addWidget(self.editor)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        self.addWidget(left_widget)
        self.addWidget(right_widget)
        self.setStretchFactor(1, 1)
        self.resize(1000, 800)

        self.setWindowIcon(QIcon("paragon.ico"))
