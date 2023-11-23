from PySide6.QtGui import QUndoCommand


class ReorderUndoCommand(QUndoCommand):
    def __init__(self, index, new_index, widget, is_faction=False):
        super().__init__()
        self.index = index
        self.new_index = new_index
        self.widget = widget
        self.is_faction = is_faction

    def undo(self):
        if self.is_faction:
            self.widget.reorder_faction(self.new_index, self.index)
        else:
            self.widget.reorder_spawn(self.new_index, self.index)

    def redo(self):
        if self.is_faction:
            self.widget.reorder_faction(self.index, self.new_index)
        else:
            self.widget.reorder_spawn(self.index, self.new_index)
