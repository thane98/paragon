from PySide2.QtWidgets import QWidget, QVBoxLayout

from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget


class DerefWidget(AbstractAutoWidget, QWidget):
    def __init__(self, state, field_id):
        AbstractAutoWidget.__init__(self, state)
        QWidget.__init__(self)

        fm = state.field_metadata[field_id]
        self.stored_type = fm["stored_type"]
        self.inner = state.generator.generate_for_type(fm["stored_type"], state)

        layout = QVBoxLayout()
        layout.addWidget(self.inner)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.field_id = field_id

    def set_target(self, rid):
        if not rid:
            self.inner.set_target(None)
        else:
            self.inner.set_target(self.data.rid(rid, self.field_id))
