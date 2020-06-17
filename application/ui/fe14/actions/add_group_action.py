class AddGroupAction:
    def __init__(self, controller, faction):
        self.controller = controller
        self.faction = faction

    def __repr__(self):
        return "<AddGroupAction %s>" % self.faction.name

    def undo(self):
        grid = self.controller.view.grid
        self.controller.dispos_model.delete_faction(self.faction)
        grid.set_chapter_data(self.controller.chapter_data)  # Force a refresh.
        self.controller.view.spawn_pane.update_target(None)
        self.controller.view.status_bar.showMessage("Undo: Add group " + self.faction.name)

    def redo(self):
        grid = self.controller.view.grid
        self.controller.dispos_model.add_existing_faction(self.faction)
        grid.set_chapter_data(self.controller.chapter_data)  # Force a refresh.
        self.controller.view.spawn_pane.update_target(None)
        self.controller.view.status_bar.showMessage("Redo: Add group " + self.faction.name)
