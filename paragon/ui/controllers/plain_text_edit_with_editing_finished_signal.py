from PySide2.QtCore import Signal
from PySide2.QtWidgets import QPlainTextEdit


class PlainTextEditWithEditingFinishedSignal(QPlainTextEdit):
    editing_finished = Signal()

    def focusOutEvent(self, e):
        super().focusOutEvent(e)
        self.editing_finished.emit()
