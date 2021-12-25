from PySide2 import QtCore
from PySide2.QtWidgets import QWidget, QFormLayout, QLabel, QLineEdit, QPlainTextEdit

from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class DependentMessagesWidget(AbstractAutoWidget, QWidget):
    def __init__(self, state, spec):
        AbstractAutoWidget.__init__(self, state)
        QWidget.__init__(self)
        self.rid = None
        self.no_write_back = False

        layout = QFormLayout()
        self.lines = []
        self.editors = []
        self.spec = spec
        for entry in spec.lines:
            label = QLabel(entry.label)
            if entry.multiline:
                edit = QPlainTextEdit()
                edit.textChanged.connect(
                    lambda e=edit, s=entry: self._on_edit(s, e.toPlainText()),
                    QtCore.Qt.UniqueConnection,
                )
            else:
                edit = QLineEdit()
                edit.textChanged.connect(
                    lambda t, s=entry: self._on_edit(s, t), QtCore.Qt.UniqueConnection
                )
            layout.addRow(label, edit)
            self.lines.append(entry)
            self.editors.append(edit)
        self.setLayout(layout)

    def _on_edit(self, spec, text):
        if not self.rid or not self.data.key(self.rid) or self.no_write_back:
            return
        key = self.data.key(self.rid)
        if key.startswith(self.spec.key_prefix):
            key = key[len(self.spec.key_prefix) :]
        message_key = spec.key % tuple([key] * spec.param_count)
        if text and spec.multiline:
            text = text.replace("\n", "\\n")
            text = text.replace("\r", "")
        if not text:
            text = None  # Make sure it's None, not empty string.
        self.data.set_message(spec.path, spec.localized, message_key, text)

    def set_target(self, rid):
        self.rid = rid
        self.no_write_back = True
        try:
            if not rid:
                # Nothing to edit.
                for editor in self.editors:
                    editor.clear()
                    editor.setDisabled(True)
            elif key := self.data.key(rid):
                if key.startswith(self.spec.key_prefix):
                    key = key[len(self.spec.key_prefix) :]

                # Have the text and the key.
                for i, spec in enumerate(self.lines):
                    editor = self.editors[i]
                    message_key = spec.key % tuple([key] * spec.param_count)
                    text = self.data.message(spec.path, spec.localized, message_key)
                    if not text:
                        if spec.multiline:
                            editor.setPlainText("")
                        else:
                            editor.setText("")
                    elif spec.multiline:
                        editor.setPlainText(text.replace("\\n", "\n"))
                    else:
                        editor.setText(text if text else "")
                    editor.setEnabled(True)
            else:
                # Something to edit, but no key...
                # Keep lines enabled, but do nothing
                # until a key is given.
                for editor in self.editors:
                    editor.clear()
                    editor.setEnabled(True)
        finally:
            self.no_write_back = False
