from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget
from paragon.ui.views.ui_record_widget import Ui_RecordWidget


class RecordWidget(AbstractAutoWidget, Ui_RecordWidget):
    def __init__(self, state, spec, field_id):
        AbstractAutoWidget.__init__(self, state)
        Ui_RecordWidget.__init__(self)
        self.field_id = field_id
        self.rid = None

        if spec.read_only:
            self.buttons_widget.hide()

        self.new_button.clicked.connect(self._on_new)
        self.delete_button.clicked.connect(self._on_delete)
        self.toggle_button.clicked.connect(self._on_toggle)

        fm = state.field_metadata[field_id]
        self.stored_type = fm["stored_type"]
        self.inner = state.generator.generate_for_type(fm["stored_type"], state)
        self.layout().addWidget(self.inner)
        self.layout().setStretch(1, 1)
        self.inner.set_target(None)
        self._update_buttons()

    def set_target(self, rid):
        self.rid = rid
        if self.rid:
            inner_rid = self.data.rid(rid, self.field_id)
            if inner_rid:
                self.inner.set_target(inner_rid)
            else:
                self.inner.set_target(None)
        else:
            self.inner.set_target(None)

    def _on_new(self):
        if self.rid:
            # Delete the old instance if one exists.
            inner_rid = self.data.rid(self.rid, self.field_id)
            if inner_rid:
                self.data.delete_instance(inner_rid)

            # Allocate a new instance.
            inner_rid = self.data.new_instance(self.stored_type)
            self.data.set_rid(self.rid, self.field_id, inner_rid)

            # Update the UI.
            self.inner.set_target(inner_rid)
            self._update_buttons()

    def _on_delete(self):
        if self.rid:
            inner_rid = self.data.rid(self.rid, self.field_id)
            if inner_rid:
                self.data.delete_instance(inner_rid)
            self.data.set_rid(self.rid, self.field_id, None)
            self.inner.set_target(None)
            self._update_buttons()

    def _on_toggle(self):
        self.inner.setVisible(not self.inner.isVisible())

    def _update_buttons(self):
        if not self.rid:
            self.new_button.setEnabled(False)
            self.delete_button.setEnabled(False)
        else:
            inner_rid = self.data.rid(self.rid, self.field_id)
            self.new_button.setEnabled(True)
            self.delete_button.setEnabled(inner_rid is not None)
