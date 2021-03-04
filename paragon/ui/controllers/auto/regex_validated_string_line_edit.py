import re

from PySide2.QtGui import QIcon, QImage, QPixmap
from PySide2.QtWidgets import QLineEdit, QAction

from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class RegexValidatedStringLineEdit(AbstractAutoWidget, QLineEdit):
    def __init__(self, state, spec, field_id):
        AbstractAutoWidget.__init__(self, state)
        QLineEdit.__init__(self)
        self.regex = re.compile(spec.regex)
        self.rid = None
        self.field_id = field_id
        self.textChanged.connect(self._on_edit)

        self.status_action = QAction()
        self.addAction(self.status_action, QLineEdit.LeadingPosition)
        self.status_action.setToolTip(spec.tooltip)

        self.set_target(None)

    def text_is_valid(self) -> bool:
        return bool(re.match(self.regex, self.text()))

    def update_icon(self):
        if self.text_is_valid():
            icon = QIcon("resources/icons/check-circle.svg")
        else:
            icon = QIcon("resources/icons/times-circle.svg")
        self.status_action.setIcon(icon)

    def set_target(self, rid):
        self.rid = rid
        if rid:
            self.setText(self.data.string(rid, self.field_id))
        else:
            self.setText("")
        self.setEnabled(rid is not None)
        self.update_icon()

    def _on_edit(self):
        self.update_icon()
        if self.rid:
            self.data.set_string(self.rid, self.field_id, self.text())
