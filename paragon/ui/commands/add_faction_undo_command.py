from PySide2.QtWidgets import QUndoCommand


class AddFactionUndoCommand(QUndoCommand):
    def __init__(self, name, widget):
        super().__init__()
        self.name = name
        self.faction = None
        self.index = None
        self.widget = widget

    def undo(self):
        self.widget.delete_faction(self.faction)

    def redo(self):
        if self.faction:
            self.widget.add_faction(faction=self.faction, index=self.index)
        else:
            self.faction, self.index = self.widget.add_faction(name=self.name)
