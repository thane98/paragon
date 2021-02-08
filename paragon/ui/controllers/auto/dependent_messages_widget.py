from PySide2.QtWidgets import QWidget, QFormLayout, QLabel, QLineEdit, QPlainTextEdit

from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


# TODO: "REFRESH" button for when the key changes?
#       Or can we listen for that somehow?
class DependentMessagesWidget(AbstractAutoWidget, QWidget):
    def __init__(self, state, spec):
        AbstractAutoWidget.__init__(self, state)
        QWidget.__init__(self)
        self.rid = None

        layout = QFormLayout()
        self.lines = []
        self.editors = []
        for entry in spec.lines:
            label = QLabel(entry.label)
            if entry.multiline:
                edit = QPlainTextEdit()
                edit.textChanged.connect(lambda e=edit, s=entry: self._on_edit(s, e.toPlainText()))
            else:
                edit = QLineEdit()
                edit.textChanged.connect(lambda t, s=entry: self._on_edit(s, t))
            layout.addRow(label, edit)
            self.lines.append(entry)
            self.editors.append(edit)
        self.setLayout(layout)

    def _on_edit(self, spec, text):
        if not self.rid or not self.data.key(self.rid):
            return
        key = self.data.key(self.rid)
        message_key = spec.key % tuple([key] * spec.param_count)
        if text and spec.multiline:
            text = text.replace("\n", "\\n")
            text = text.replace("\r", "")
        if not text:
            text = None  # Make sure it's None, not empty string.
        self.data.set_message(spec.path, spec.localized, message_key, text)

    def set_target(self, rid):
        self.rid = rid
        if not rid:
            # Nothing to edit.
            for editor in self.editors:
                editor.clear()
                editor.setDisabled(True)
        elif key := self.data.key(rid):
            # Have the text and the key.
            for i, spec in enumerate(self.lines):
                editor = self.editors[i]
                message_key = spec.key % tuple([key] * spec.param_count)
                print(message_key)
                text = self.data.message(spec.path, spec.localized, message_key)
                if not text:
                    editor.setText("")
                elif spec.multiline:
                    editor.setPlainText(text.replace("\\n", "\n"))
                else:
                    editor.setText(text if text else "")
        else:
            # Something to edit, but no key...
            # Keep lines enabled, but do nothing
            # until a key is given.
            for editor in self.editors:
                editor.clear()
                editor.setEnabled(True)


