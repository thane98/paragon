class PropertyWidget:
    def __init__(self, target_property_name):
        self.target_property_name = target_property_name
        self.target = None
        self.form = None

    def commit(self, value):
        if self.target:
            self.target[self.target_property_name].value = value

    def _get_target_value(self):
        return self.target[self.target_property_name].value

    def update_target(self, new_target):
        self.target = new_target
        self._on_target_changed()

    def _on_target_changed(self):
        raise NotImplemented
