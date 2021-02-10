from PySide2.QtWidgets import QUndoCommand


class PasteSpawnUndoCommand(QUndoCommand):
    def __init__(self, types, clipboard, spawn, widget):
        super().__init__()
        self.clipboard = clipboard
        self.spawn = spawn
        self.widget = widget
        self.original = types.instantiate("Spawn")
        spawn.copy_to(self.original)

    def undo(self):
        self.widget.paste_spawn(self.original, self.spawn)

    def redo(self):
        self.widget.paste_spawn(self.clipboard, self.spawn)
