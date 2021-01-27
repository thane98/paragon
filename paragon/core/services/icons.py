from PySide2 import QtCore


class Icons:
    def __init__(self, data):
        self.data = data
        self.models = {}
        self.loaded = False

    def _load(self):
        raise NotImplementedError

    def icon(self, rid):
        if not self.loaded:
            self.loaded = True
            self._load()
        key = self.to_key(rid)
        row = self.to_row(rid, key)
        if key not in self.models or row is None:
            return None
        else:
            index = self.models[key].index(row, 0)
            return self.models[key].data(index, QtCore.Qt.DecorationRole)

    def model(self, model_id):
        if not self.loaded:
            self.loaded = True
            self._load()
        return self.models.get(model_id)

    def to_row(self, rid, key):
        raise NotImplementedError

    def to_key(self, rid):
        return self.data.icon_category(rid)

    def register(self, key, icons):
        self.models[key] = icons
