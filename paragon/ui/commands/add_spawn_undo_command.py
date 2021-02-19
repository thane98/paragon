from PySide2.QtWidgets import QUndoCommand


class AddSpawnUndoCommand(QUndoCommand):
    def __init__(self, faction, widget):
        super().__init__()
        self.faction = faction
        self.spawn = None
        self.index = None
        self.widget = widget

    def undo(self):
        self.widget.delete_spawn(self.spawn)

    def redo(self):
        self.spawn, self.index = self.widget.add_spawn(
            self.faction, self.spawn, self.index
        )
