from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import (
    QWidget,
    QListWidget,
    QVBoxLayout,
    QSplitter,
    QPlainTextEdit,
    QComboBox,
    QStatusBar,
    QPushButton,
)

from paragon.ui.views import layouts


class PlainTextEditWithLostFocusSignal(QPlainTextEdit):
    lostFocus = Signal()

    def focusOutEvent(self, e):
        self.lostFocus.emit()
        super().focusOutEvent(e)


class Ui_LayeredDirEditor(QSplitter):
    def __init__(self, has_sub_entries):
        super().__init__()

        self.list_widget = QListWidget()

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.list_widget)
        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        self.entries_box = QComboBox()
        self.entries_box.setMinimumWidth(300)
        self.add_entry_button = QPushButton("+")
        self.delete_entry_button = QPushButton("-")
        self.editor = PlainTextEditWithLostFocusSignal()
        font = QFont()
        font.setPointSize(10)
        self.editor.setFont(font)
        self.status_bar = QStatusBar()

        top_layout = layouts.make_hbox(
            [self.entries_box, self.add_entry_button, self.delete_entry_button],
            margins=False,
        )
        top_layout.setStretch(0, 1)

        right_layout = QVBoxLayout()
        if has_sub_entries:
            right_layout.addLayout(top_layout)
        right_layout.addWidget(self.editor)
        right_layout.addWidget(self.status_bar)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        self.addWidget(left_widget)
        self.addWidget(right_widget)
        self.setStretchFactor(1, 1)
        self.resize(1000, 800)

        self.setWindowIcon(QIcon("paragon.ico"))
