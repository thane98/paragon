from PySide6.QtGui import QUndoCommand


class DeleteFactionUndoCommand(QUndoCommand):
    def __init__(self, faction, widget, index):
        super().__init__()
        self.faction = faction
        self.widget = widget
        self.index = index

    def undo(self):
        self.widget.add_faction(faction=self.faction, index=self.index)

    def redo(self):
        self.widget.delete_faction(self.faction)
