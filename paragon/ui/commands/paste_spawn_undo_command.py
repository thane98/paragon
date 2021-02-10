from PySide2.QtWidgets import QUndoCommand


class PasteSpawnUndoCommand(QUndoCommand):
    def __init__(self, gd, source, dest, widget):
        super().__init__()
        self.source = source
        self.dest = dest
        self.widget = widget

        # Keep a copy of the dest so we can undo.
        self.original = gd.new_instance("Spawn")
        gd.copy(self.dest, self.original, [])

    def undo(self):
        self.widget.paste_spawn(self.original, self.dest)

    def redo(self):
        self.widget.paste_spawn(self.source, self.dest)
