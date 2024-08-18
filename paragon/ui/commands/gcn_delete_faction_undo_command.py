from PySide6.QtGui import QUndoCommand


class GcnDeleteFactionUndoCommand(QUndoCommand):
    def __init__(self, difficulty_item, faction, widget, index):
        super().__init__()
        self.difficulty = difficulty_item
        self.faction = faction
        self.widget = widget
        self.index = index

    def undo(self):
        self.widget.add_faction(self.difficulty, faction=self.faction, index=self.index)

    def redo(self):
        self.widget.delete_faction(self.faction)
