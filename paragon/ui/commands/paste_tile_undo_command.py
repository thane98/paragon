from PySide6.QtGui import QUndoCommand


class PasteTileUndoCommand(QUndoCommand):
    def __init__(self, gd, source, dest, widget):
        super().__init__()
        self.dest = dest
        self.widget = widget

        self.original = gd.new_instance("Tile", self.gd.store_number_of(source))
        gd.copy(self.dest, self.original, [])
        self.source = gd.new_instance("Tile", self.gd.store_number_of(dest))
        gd.copy(source, self.source, [])

    def undo(self):
        self.widget.paste_tile(self.original, self.dest)

    def redo(self):
        self.widget.paste_tile(self.source, self.dest)
