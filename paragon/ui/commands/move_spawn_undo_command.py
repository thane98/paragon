from PySide2.QtWidgets import QUndoCommand


class MoveSpawnUndoCommand(QUndoCommand):
    def __init__(self, old_coord, new_coord, spawn, coord_2, widget):
        super().__init__()
        self.old = old_coord
        self.new = new_coord
        self.spawn = spawn
        self.coord_2 = coord_2
        self.widget = widget

    def mergeWith(self, other) -> bool:
        if other is MoveSpawnUndoCommand:
            return (
                other.old == self.old
                and other.new == self.new
                and other.spawn == self.spawn
                and other.coord_2 == self.coord_2
            )
        return False

    def undo(self):
        self.widget.move_spawn(self.old[1], self.old[0], self.spawn, self.coord_2)

    def redo(self):
        self.widget.move_spawn(self.new[1], self.new[0], self.spawn, self.coord_2)
