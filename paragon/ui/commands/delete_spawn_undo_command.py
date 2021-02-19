from PySide2.QtWidgets import QUndoCommand


class DeleteSpawnUndoCommand(QUndoCommand):
    def __init__(self, faction, spawn, widget, index):
        super().__init__()
        self.faction = faction
        self.spawn = spawn
        self.widget = widget
        self.index = index

    def undo(self):
        self.widget.add_spawn(self.faction, spawn=self.spawn, index=self.index)

    def redo(self):
        self.widget.delete_spawn(self.spawn)
