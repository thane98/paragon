from PySide2 import QtWidgets
from PySide2.QtWidgets import QWidget, QFormLayout


class ObjectEditor(QWidget):
    def __init__(self, driver, module):
        super().__init__()
        self.driver = driver
        self.module = module
        self.element = self.module.element
        self.setWindowTitle(module.name)

        layout = QFormLayout(self)
        self.editors = []
        for (key, prop) in self.element.items():
            label = QtWidgets.QLabel(key)
            editor = prop.create_editor()
            self.editors.append(editor)
            editor.update_target(self.element)
            layout.addRow(label, editor)
        self.setLayout(layout)
