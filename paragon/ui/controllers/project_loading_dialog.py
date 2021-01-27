from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QProgressDialog


class ProjectLoadingDialog(QProgressDialog):
    def __init__(self, project):
        super().__init__(f"Loading project {project.name}...", "Cancel", 0, 0)
        self.setAutoClose(True)
        self.setModal(True)
        self.setWindowTitle("Paragon - Loading...")
        self.setWindowIcon(QIcon("paragon.ico"))
