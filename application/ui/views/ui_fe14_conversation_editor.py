from PySide2 import QtGui
from PySide2.QtWidgets import QFrame, QFormLayout, QLineEdit, QCheckBox, QMainWindow, QHBoxLayout, QPushButton, \
    QVBoxLayout, QTabWidget, QStatusBar, QWidget, QToolBar, QListView, QTextEdit

from ui.widgets.fe14_conversation_player import FE14ConversationPlayer


class Ui_FE14ConversationEditor(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.player = FE14ConversationPlayer()
        self.visual_splitter_1 = QFrame()
        self.visual_splitter_1.setFrameShape(QFrame.HLine)
        self.visual_splitter_1.setFrameShadow(QFrame.Sunken)

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setAlignment(QtGui.Qt.AlignCenter)
        self.save_button = QPushButton(text="Save")
        self.preview_button = QPushButton("Preview")
        self.buttons_layout.addWidget(self.save_button)
        self.buttons_layout.addWidget(self.preview_button)
        self.visual_splitter_2 = QFrame()
        self.visual_splitter_2.setFrameShape(QFrame.HLine)
        self.visual_splitter_2.setFrameShadow(QFrame.Sunken)

        self.avatar_form = QFormLayout()
        self.avatar_name_editor = QLineEdit()
        self.avatar_is_female_check = QCheckBox()
        self.avatar_form.addRow("Avatar Name", self.avatar_name_editor)
        self.avatar_form.addRow("Avatar Is Female", self.avatar_is_female_check)

        self.visual_splitter_3 = QFrame()
        self.visual_splitter_3.setFrameShape(QFrame.HLine)
        self.visual_splitter_3.setFrameShadow(QFrame.Sunken)

        self.conversation_list = QListView()

        self.left_layout = QVBoxLayout()
        self.left_layout.addWidget(self.player)
        self.left_layout.addWidget(self.visual_splitter_1)
        self.left_layout.addLayout(self.buttons_layout)
        self.left_layout.addWidget(self.visual_splitter_2)
        self.left_layout.addLayout(self.avatar_form)
        self.left_layout.addWidget(self.visual_splitter_3)
        self.left_layout.addWidget(self.conversation_list)
        self.left_layout.setStretch(0, 0)
        self.left_layout.setStretch(1, 0)
        self.left_layout.setStretch(2, 0)
        self.left_layout.setStretch(3, 0)
        self.left_layout.setStretch(4, 0)
        self.left_layout.setStretch(5, 0)
        self.left_layout.setStretch(6, 1)

        self.text_area = QTextEdit()

        self.main_layout = QHBoxLayout()
        self.main_layout.addLayout(self.left_layout)
        self.main_layout.addWidget(self.text_area)
        self.main_layout.setStretch(0, 0)
        self.main_layout.setStretch(1, 1)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.tool_bar = QToolBar()
        self.addToolBar(self.tool_bar)
        self.setCentralWidget(self.central_widget)
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.resize(900, 500)
