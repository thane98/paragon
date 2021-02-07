from paragon.model.list_field_model import ListFieldModel


class Models:
    def __init__(self, gd, icons):
        self.gd = gd
        self.icons = icons
        self.models = {}

    def get(self, rid, field_id):
        key = (rid, field_id)
        if key in self.models:
            return self.models[key]
        else:
            typename = self.gd.type_of(rid)
            metadata = self.gd.type_metadata(typename)
            model = ListFieldModel(self.gd, self.icons, rid, field_id, metadata["display_function"])
            self.models[key] = model
            return model
