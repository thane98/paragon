import os

from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QLineEdit

from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class FileInput(AbstractAutoWidget, QLineEdit):
    def __init__(self, state, spec, field_id):
        AbstractAutoWidget.__init__(self, state)
        QLineEdit.__init__(self)
        self.dirs = spec.dirs
        self.optional = spec.optional
        self.suffix = spec.suffix
        self.rid = None
        self.field_id = field_id
        self.textChanged.connect(self._on_edit)

        self.status_action = QAction()
        self.addAction(self.status_action, QLineEdit.LeadingPosition)

        self.set_target(None)

    def text_is_valid(self) -> bool:
        if not self.text() and self.optional:
            self.setToolTip("")
            return True
        else:
            for path in self.dirs:
                full_path = os.path.join(path, self.text()) + self.suffix
                if self.data.file_exists(full_path, False):
                    self.setToolTip(os.path.normpath(full_path))
                    return True
            self.setToolTip("")
            return False

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
            text = self.text() if self.text() else None
            self.data.set_string(self.rid, self.field_id, text)
