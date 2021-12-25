from PySide2.QtCore import Signal
from PySide2.QtGui import QIcon, QFont
from PySide2.QtWidgets import (
    QWidget,
    QListWidget,
    QVBoxLayout,
    QSplitter,
    QPlainTextEdit,
    QComboBox,
    QStatusBar,
)


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
        self.editor = PlainTextEditWithLostFocusSignal()
        font = QFont()
        font.setPointSize(10)
        self.editor.setFont(font)
        self.status_bar = QStatusBar()

        right_layout = QVBoxLayout()
        if has_sub_entries:
            right_layout.addWidget(self.entries_box)
        right_layout.addWidget(self.editor)
        right_layout.addWidget(self.status_bar)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        self.addWidget(left_widget)
        self.addWidget(right_widget)
        self.setStretchFactor(1, 1)
        self.resize(1000, 800)

        self.setWindowIcon(QIcon("paragon.ico"))
