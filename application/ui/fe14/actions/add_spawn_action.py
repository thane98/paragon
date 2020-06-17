class AddSpawnAction:
    def __init__(self, controller, faction, spawn):
        self.controller = controller
        self.spawn = spawn
        self.faction = faction

    def __repr__(self):
        return "<AddSpawnAction %s, %s>" % (self.spawn.get_display_name(), self.faction.name)

    def undo(self):
        grid = self.controller.view.grid
        self.controller.dispos_model.delete_spawn(self.spawn)
        grid.delete_spawn(self.spawn)
        self.controller.view.status_bar.showMessage("Undo: Add spawn " + self.spawn.get_display_name())

    def redo(self):
        self.controller.dispos_model.add_spawn_to_faction(self.faction, self.spawn)
        spawn = self.faction.spawns[-1]
        self.controller.view.grid.add_spawn_to_map(spawn)
        self.controller.view.status_bar.showMessage("Redo: Add spawn " + self.spawn.get_display_name())
