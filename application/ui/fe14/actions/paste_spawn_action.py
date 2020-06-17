class PasteSpawnAction:
    def __init__(self, controller, spawn1, spawn2):
        self.controller = controller
        self.spawn1_capture = spawn1.duplicate()
        self.spawn2_capture = spawn2.duplicate()
        self.spawn1 = spawn1

    def __repr__(self):
        return "<PasteSpawnAction %s, %s>" % (self.spawn1.get_display_name(), self.spawn2_capture.get_display_name())

    def undo(self):
        self.controller.dispos_model.copy_spawn_and_ignore_coordinates(self.spawn1_capture, self.spawn1)
        self.controller.view.grid.refresh_cell_from_spawn(self.spawn1)
        self.controller.view.status_bar.showMessage(
            "Undo: Copy %s to %s" % (self.spawn2_capture.get_display_name(), self.spawn1.get_display_name()))

    def redo(self):
        self.controller.dispos_model.copy_spawn_and_ignore_coordinates(self.spawn2_capture, self.spawn1)
        self.controller.view.grid.refresh_cell_from_spawn(self.spawn1)
        self.controller.view.status_bar.showMessage(
            "Redo: Copy %s to %s" % (self.spawn2_capture.get_display_name(), self.spawn1.get_display_name()))
