from PySide2.QtWidgets import QUndoCommand
from paragon.model.coordinate_change_type import CoordinateChangeType


class MoveSpawnUndoCommand(QUndoCommand):
    def __init__(self, old_coord, new_coord, spawn, coordinate_change_type, widget):
        super().__init__()
        self.old = old_coord
        self.new = new_coord
        self.spawn = spawn
        self.coordinate_change_type = coordinate_change_type
        self.widget = widget

    def mergeWith(self, other) -> bool:
        if other is MoveSpawnUndoCommand:
            return (
                other.old == self.old
                and other.new == self.new
                and other.spawn == self.spawn
                and other.coordinate_change_type == self.coordinate_change_type
            )
        return False

    def undo(self):
        self.widget.move_spawn(
            self.old[1], self.old[0], self.spawn, self.coordinate_change_type
        )

    def redo(self):
        self.widget.move_spawn(
            self.new[1], self.new[0], self.spawn, self.coordinate_change_type
        )
