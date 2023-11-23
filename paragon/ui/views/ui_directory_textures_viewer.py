from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QTreeView, QHBoxLayout, QComboBox, QVBoxLayout
from paragon.ui.controllers.scene_graphics_view import ImageGraphicsView


class Ui_DirectoryTexturesViewer(QWidget):
    def __init__(self):
        super().__init__()

        self.layers_box = QComboBox()
        self.layers_box.addItems(["ROM", "Output Folder"])

        self.tree_view = QTreeView()
        self.image_view = ImageGraphicsView()

        self.left_layout = QVBoxLayout()
        self.left_layout.addWidget(self.layers_box)
        self.left_layout.addWidget(self.tree_view)

        self.main_layout = QHBoxLayout()
        self.main_layout.addLayout(self.left_layout)
        self.main_layout.addWidget(self.image_view)
        self.main_layout.setStretch(1, 1)

        self.setLayout(self.main_layout)
        self.resize(1200, 800)
        self.setWindowIcon(QIcon("paragon.ico"))
