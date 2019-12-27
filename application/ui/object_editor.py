import logging

from PySide2 import QtWidgets
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QFormLayout, QScrollArea, QVBoxLayout


class ObjectEditor(QWidget):
    def __init__(self, driver, module):
        super().__init__()
        self.driver = driver
        self.module = module
        self.element = self.module.element
        self.setWindowTitle(module.name)
        self.setWindowIcon(QIcon("paragon.ico"))

        central_layout = QVBoxLayout()
        scroll_area = QScrollArea()
        form_widget = QWidget()

        layout = QFormLayout(self)
        self.editors = []
        for (key, prop) in self.element.items():
            label = QtWidgets.QLabel(key)
            editor = prop.create_editor()
            self.editors.append(editor)
            editor.update_target(self.element)
            layout.addRow(label, editor)
        form_widget.setLayout(layout)
        scroll_area.setWidget(form_widget)
        scroll_area.setWidgetResizable(True)
        central_layout.addWidget(scroll_area)

        self.setLayout(central_layout)

        logging.info("Generated ObjectEditor for " + self.module.name)
