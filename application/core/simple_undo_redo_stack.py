from PySide2.QtCore import Signal, QObject


class SimpleUndoRedoStack(QObject):
    stack_state_changed = Signal()

    def __init__(self):
        super().__init__()
        self._actions = []
        self._next = -1
        self._disable_push = False

    def can_undo(self) -> bool:
        return self._next in range(0, len(self._actions))

    def can_redo(self) -> bool:
        return (self._next + 1) in range(0, len(self._actions))

    def push_action(self, action):
        if self._disable_push:
            return
        if self._next != -1 and self._next < len(self._actions) - 1:
            del self._actions[self._next + 1:]
        self._actions.append(action)
        self._next += 1
        self.stack_state_changed.emit()

    def undo(self):
        if self.can_undo():
            self._disable_push = True
            try:
                self._actions[self._next].undo()
                self.stack_state_changed.emit()
            except:
                pass
            self._next -= 1
            self._disable_push = False
        else:
            raise IndexError("Cannot undo at the bottom of the stack.")

    def redo(self):
        if self.can_redo():
            self._next += 1
            self._disable_push = True
            try:
                self._actions[self._next].redo()
                self.stack_state_changed.emit()
            except:
                pass
            self._disable_push = False
        else:
            raise IndexError("Cannot redo at the top of the stack.")
