class DeleteSpawnAction:
    def __init__(self, controller, faction, spawn):
        self.controller = controller
        self.spawn = spawn
        self.faction = faction

    def __repr__(self):
        return "<DeleteSpawnAction %s, %s>" % (self.spawn.get_display_name(), self.faction.name)

    def undo(self):
        self.controller.dispos_model.add_spawn_to_faction(self.faction, spawn=self.spawn)
        spawn = self.faction.spawns[-1]
        self.controller.view.grid.add_spawn_to_map(spawn)
        self.controller.view.status_bar.showMessage("Undo: Delete spawn " + self.spawn.get_display_name())

    def redo(self):
        grid = self.controller.view.grid
        self.controller.dispos_model.delete_spawn(self.spawn)
        grid.delete_spawn(self.spawn)
        self.controller.view.status_bar.showMessage("Redo: Delete spawn " + self.spawn.get_display_name())
