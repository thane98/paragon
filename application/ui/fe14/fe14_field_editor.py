from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QTabWidget

from services.service_locator import locator
from ui.object_editor import ObjectEditor
from ui.simple_editor import SimpleEditor


class FE14FieldEditor(QTabWidget):
    def __init__(self, modules, field_name: str):
        super().__init__()
        self.setWindowTitle("Field Editor - " + field_name)
        self.setWindowIcon(QIcon("paragon.ico"))
        self.modules = modules
        self.service = locator.get_scoped("FieldService")
        self.parts_editor = SimpleEditor(self.modules[0])
        self.refer_editor = SimpleEditor(self.modules[1])
        self.files_editor = SimpleEditor(self.modules[2])
        self.gamedata_field_editor = ObjectEditor(self.modules[3])
        self.addTab(self.parts_editor, "Parts")
        self.addTab(self.refer_editor, "Refer")
        self.addTab(self.files_editor, "Files")
        self.addTab(self.gamedata_field_editor, "Config")
        self.resize(1000, 600)
