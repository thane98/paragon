from PySide6.QtGui import QUndoCommand


class GcnAddFactionUndoCommand(QUndoCommand):
    def __init__(self, difficulty, name, widget):
        super().__init__()
        self.name = name
        self.difficulty = difficulty
        self.faction = None
        self.index = None
        self.widget = widget

    def undo(self):
        self.widget.delete_faction(self.faction)

    def redo(self):
        if self.faction:
            self.widget.add_faction(
                self.difficulty, faction=self.faction, index=self.index
            )
        else:
            self.faction, self.index = self.widget.add_faction(
                self.difficulty, name=self.name
            )
