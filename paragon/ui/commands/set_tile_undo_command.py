from PySide2.QtWidgets import QUndoCommand


class SetTileUndoCommand(QUndoCommand):
    def __init__(self, widget, row, col, tile, original):
        super().__init__()
        self.widget = widget
        self.row = row
        self.col = col
        self.tile = tile
        self.original = original

    def undo(self):
        self.widget.set_tile(self.row, self.col, self.original)

    def redo(self):
        self.widget.set_tile(self.row, self.col, self.tile)
