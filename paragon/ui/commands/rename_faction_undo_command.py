from PySide2.QtWidgets import QUndoCommand


class RenameFactionUndoCommand(QUndoCommand):
    def __init__(self, faction, old_name, new_name, widget):
        super().__init__()
        self.widget = widget
        self.faction = faction
        self.old_name = old_name
        self.new_name = new_name

    def undo(self):
        self.widget.rename_faction(self.faction, self.old_name)

    def redo(self):
        self.widget.rename_faction(self.faction, self.new_name)
