from PySide2 import QtCore
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QLineEdit, QListView, QVBoxLayout, QGroupBox, QTabWidget, QHBoxLayout, QFrame, \
    QGraphicsView, QMainWindow, QToolBar, QAction, QScrollArea

from ui.widgets.portrait_viewer import PortraitViewer


class Ui_FE14CharacterEditor(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.setFixedWidth(225)
        self.characters_list_view = QListView()
        self.characters_list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.characters_list_view.setFixedWidth(225)
        self.characters_list_layout = QVBoxLayout()
        self.characters_list_layout.addWidget(self.search_bar)
        self.characters_list_layout.addWidget(self.characters_list_view)

        self.character_details_box = QGroupBox(title="Character Details")
        self.portrait_display = QGraphicsView()
        self.portrait_display.setFixedSize(140, 140)
        self.character_details_form_contents_1 = QWidget()
        self.character_details_form_contents_2 = QWidget()
        self.character_details_layout = QHBoxLayout()
        self.character_details_layout.addWidget(self.portrait_display)
        self.character_details_layout.addWidget(self.character_details_form_contents_1)
        self.character_details_layout.addWidget(self.character_details_form_contents_2)
        self.character_details_box.setLayout(self.character_details_layout)
        self.character_details_box.setFixedHeight(200)

        self.tab_widget = QTabWidget()
        self.ids_tab = QWidget()
        self.classes_tab = QWidget()
        self.stats_tab = QScrollArea()
        self.skills_tab = QScrollArea()
        self.misc_tab = QScrollArea()
        self.portraits_tab = PortraitViewer()

        self.stats_contents = QWidget()
        self.stats_tab.setWidget(self.stats_contents)
        self.stats_tab.setWidgetResizable(True)
        self.stats_layout = QVBoxLayout()
        self.stats_layout.setAlignment(QtCore.Qt.AlignTop)
        self.stats_contents.setLayout(self.stats_layout)

        self.skills_contents = QWidget()
        self.skills_tab.setWidget(self.skills_contents)
        self.skills_tab.setWidgetResizable(True)

        self.misc_contents = QWidget()
        self.misc_tab.setWidget(self.misc_contents)
        self.misc_tab.setWidgetResizable(True)
        self.misc_layout = QVBoxLayout()
        self.misc_layout.setAlignment(QtCore.Qt.AlignTop)
        self.misc_contents.setLayout(self.misc_layout)

        self.tab_widget.addTab(self.ids_tab, "IDs")
        self.tab_widget.addTab(self.classes_tab, "Classes")
        self.tab_widget.addTab(self.stats_tab, "Stats")
        self.tab_widget.addTab(self.skills_tab, "Skills")
        self.tab_widget.addTab(self.misc_tab, "Misc.")
        self.tab_widget.addTab(self.portraits_tab, "Portraits")

        self.editor_layout = QVBoxLayout()
        self.editor_layout.addWidget(self.character_details_box)
        self.editor_layout.addWidget(self.tab_widget)

        self.main_layout = QHBoxLayout()
        self.main_layout.addLayout(self.characters_list_layout)
        self.visual_splitter = QFrame()
        self.visual_splitter.setFrameShape(QFrame.VLine)
        self.visual_splitter.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(self.visual_splitter)
        self.main_layout.addLayout(self.editor_layout)

        self.tool_bar = QToolBar()
        self.action_add = QAction(text="Add")
        self.action_remove = QAction(text="Remove")
        self.action_copy_to = QAction(text="Copy To")
        self.tool_bar.addActions([
            self.action_add,
            self.action_remove,
            self.action_copy_to
        ])

        self.addToolBar(self.tool_bar)

        self.resize(1000, 600)
        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setWindowTitle("Character Editor")
        self.setWindowIcon(QIcon("paragon.ico"))
        self.setCentralWidget(central_widget)
