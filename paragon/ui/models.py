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
            display_function = self._get_display_function(rid, field_id)
            model = ListFieldModel(
                self.gd, self.icons, rid, field_id, display_function
            )
            self.models[key] = model
            return model

    def _get_display_function(self, rid, field_id):
        typename = self.gd.type_of(rid)
        metadata = self.gd.metadata_from_field_id(typename, field_id)
        if not metadata:
            return None
        stored_type = metadata.get("stored_type")
        if not stored_type:
            return None
        metadata = self.gd.type_metadata(stored_type)
        return metadata["display_function"] if metadata else None
