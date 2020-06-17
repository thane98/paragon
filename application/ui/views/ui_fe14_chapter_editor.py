from PySide2.QtWidgets import QMainWindow, QToolBar, QAction, QListView, QLineEdit, QVBoxLayout, QTabWidget, QWidget, QHBoxLayout, QFrame

from ui.fe14.fe14_chapter_config_tab import FE14ChapterConfigTab
from ui.fe14.fe14_character_editor import FE14CharacterEditor
from ui.fe14.fe14_conversation_editor import FE14ConversationEditor
from ui.fe14.fe14_map_editor import FE14MapEditor
from ui.views.ui_fe14_map_editor import Ui_FE14MapEditor


class Ui_FE14ChapterEditor(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)
        self.add_chapter_action = QAction("Add Chapter")
        self.hide_selector_action = QAction("Toggle Selection Pane")
        self.toolbar.addAction(self.add_chapter_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.hide_selector_action)

        self.selector_layout = QVBoxLayout()
        self.chapter_search_bar = QLineEdit()
        self.chapter_search_bar.setPlaceholderText("Search...")
        self.chapter_list_view = QListView()
        self.selector_layout.addWidget(self.chapter_search_bar)
        self.selector_layout.addWidget(self.chapter_list_view)
        self.selector_widget = QWidget()
        self.selector_widget.setLayout(self.selector_layout)
        self.selector_widget.setFixedWidth(225)

        self.config_tab = FE14ChapterConfigTab()
        self.map_tab = FE14MapEditor()
        self.characters_tab = FE14CharacterEditor(is_person=True)
        self.conversation_tab = FE14ConversationEditor()
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.config_tab, "Config")
        self.tab_widget.addTab(self.map_tab, "Map")
        self.tab_widget.addTab(self.characters_tab, "Characters")
        self.tab_widget.addTab(self.conversation_tab, "Text")

        self.main_layout = QHBoxLayout()
        self.main_widget = QWidget()
        self.visual_splitter = QFrame()
        self.visual_splitter.setFrameShape(QFrame.VLine)
        self.visual_splitter.setFrameShadow(QFrame.Sunken)
        self.main_widget.setLayout(self.main_layout)
        self.main_layout.addWidget(self.selector_widget)
        self.main_layout.addWidget(self.visual_splitter)
        self.main_layout.addWidget(self.tab_widget)
        self.setCentralWidget(self.main_widget)
