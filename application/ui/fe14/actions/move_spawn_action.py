from copy import deepcopy


class MoveSpawnAction:
    def __init__(self, spawn, old_position, new_position, coordinate_key, controller):
        self.controller = controller
        self.spawn = spawn
        self.old_position = deepcopy(old_position)
        self.new_position = deepcopy(new_position)
        self.coordinate_key = coordinate_key

    def __repr__(self):
        return "<MoveSpawnAction %s, %s, [%d, %d], [%d, %d]>" \
            % (self.spawn.get_display_name(), self.coordinate_key, self.old_position[0],
               self.old_position[1], self.new_position[0], self.new_position[1])

    def undo(self):
        self._move_unit(self.old_position, True)

    def redo(self):
        self._move_unit(self.new_position, False)

    def _move_unit(self, position, is_undo):
        grid = self.controller.view.grid
        if grid.coordinate_key != self.coordinate_key:
            grid.toggle_coordinate_key()
        grid.select_spawn(self.spawn)
        grid.update_focused_spawn_position(position, self.coordinate_key)

        prefix = "Undo" if is_undo else "Redo"
        message = "%s: Update position of %s to (%d, %d)" \
                  % (prefix, self.spawn.get_display_name(), position[0], position[1])
        self.controller.view.status_bar.showMessage(message, 5000)
