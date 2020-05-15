import logging

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QScrollArea, QVBoxLayout

from ui.property_form import PropertyForm


class ObjectEditor(QWidget):
    def __init__(self, module):
        super().__init__()
        self.module = module
        self.element = self.module.element
        self.setWindowTitle(module.name)
        self.setWindowIcon(QIcon("paragon.ico"))

        central_layout = QVBoxLayout()
        scroll_area = QScrollArea()
        form_widget = QWidget()

        self.editors = []
        self.property_form = PropertyForm(self.element)
        self.property_form.update_target(self.element)
        form_widget.setLayout(self.property_form)
        scroll_area.setWidget(form_widget)
        scroll_area.setWidgetResizable(True)
        central_layout.addWidget(scroll_area)
        self.setLayout(central_layout)

        logging.info("Generated ObjectEditor for " + self.module.name)

    def show(self):
        if self.element:
            self.property_form.update_target(self.element)
        super().show()
