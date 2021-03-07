import ctypes

from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class AbstractSpinBoxes(AbstractAutoWidget):
    def __init__(self, state, field_id):
        AbstractAutoWidget.__init__(self, state)
        fm = state.field_metadata[field_id]
        self.length = fm["length"]
        self.editors = []
        self.field_id = field_id
        self.rid = None

    def save(self):
        if self.rid:
            buffer = self.data.bytes(self.rid, self.field_id)
            for i in range(0, len(self.editors)):
                value = ctypes.c_uint8(self.editors[i].value()).value
                buffer[i] = value
            self.data.set_bytes(self.rid, self.field_id, buffer)

    def set_target(self, rid):
        self.rid = rid
        for editor in self.editors:
            editor.blockSignals(True)
        try:
            if self.rid:
                value = self.data.bytes(rid, self.field_id)
                buffer = list(map(lambda x: ctypes.c_int8(x).value, value))
            else:
                buffer = [0] * self.length
            for i in range(0, len(buffer)):
                self.editors[i].setValue(buffer[i])
            self._post_set_target()
        finally:
            for editor in self.editors:
                editor.blockSignals(False)

    def value(self):
        res = []
        for editor in self.editors:
            value = ctypes.c_uint8(editor.value()).value
            res.append(value)
        return res

    def _post_set_target(self):
        raise NotImplementedError
