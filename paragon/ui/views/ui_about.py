from PySide6 import QtGui
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QLabel, QVBoxLayout, QDialog


class Ui_About(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.title_label = QLabel("Paragon")
        self.title_label.setAlignment(QtGui.Qt.AlignCenter)
        font = QFont(self.title_label.font())
        font.setPointSize(24)
        self.title_label.setFont(font)

        self.about_label = QLabel("A toolkit for editing FE13, FE14, and FE15.")
        self.thanks_label = QLabel("Special thanks to:")

        thanks_contents = ""
        for n in [
            "Moonling",
            "Lazy",
            "muhmuhten",
            "DeathChaos",
            "TildeHat",
            "AmbiguousPresence",
            "SciresM",
        ]:
            thanks_contents += f"<li>{n}</li>"
        self.thanks_contents_label = QLabel(f"<ul>{thanks_contents}</ul><br/>")

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.about_label)
        self.main_layout.addWidget(self.thanks_label)
        self.main_layout.addWidget(self.thanks_contents_label)

        self.setWindowTitle("Paragon - About")
        self.setWindowIcon(QIcon("paragon.ico"))
        self.setLayout(self.main_layout)
        self.setModal(True)
        self.setFixedSize(400, 250)
