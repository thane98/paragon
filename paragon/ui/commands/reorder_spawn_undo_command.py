from PySide2.QtWidgets import QUndoCommand


class ReorderSpawnUndoCommand(QUndoCommand):
    def __init__(self, index, new_index, widget):
        super().__init__()
        self.index = index
        self.new_index = new_index
        self.widget = widget

    def undo(self):
        self.widget.reorder_spawn(self.new_index, self.index)

    def redo(self):
        self.widget.reorder_spawn(self.index, self.new_index)
