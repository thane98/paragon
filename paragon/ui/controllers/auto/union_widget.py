from PySide2.QtWidgets import QRadioButton, QButtonGroup
from paragon.model.auto_generator_state import AutoGeneratorState

from paragon.ui import utils

from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget
from paragon.ui.views.ui_union_widget import Ui_UnionWidget


class UnionWidget(AbstractAutoWidget, Ui_UnionWidget):
    def __init__(self, state, field_id):
        AbstractAutoWidget.__init__(self, state)
        Ui_UnionWidget.__init__(self)

        self.rid = None
        self.field_id = field_id
        self.inner = None

        # Create widgets for each variant.
        self.widgets = []
        self.variant_group = QButtonGroup(self)
        self.buttons = []
        fm = state.field_metadata[self.field_id]
        gen_state = AutoGeneratorState(
            main_state=self.ms,
            game_state=self.gs,
            generator=state.generator,
            type_metadata=state.type_metadata,
            field_metadata={},
            typename=state.typename
        )
        for i, variant in enumerate(fm["variants"]):
            # Create the radio button.
            label = utils.capitalize(variant["id"], variant["name"])
            button = QRadioButton(label)
            self.variant_group.addButton(button)
            self.buttons.append(button)
            button.clicked.connect(lambda index=i: self.set_active_variant(index))

            # Create the widget.
            gen_state.field_metadata[field_id] = variant
            widget = state.generator.generate(gen_state, field_id)
            self.widgets.append(widget)

            # Add a row to the form.
            self.layout().addRow(button, widget)

        self.set_active_variant(0)

    def set_target(self, rid):
        self.rid = rid
        if rid:
            self.set_active_variant(self.data.active_variant(rid, self.field_id))
        else:
            self.set_active_variant(0)

    def set_active_variant(self, variant):
        # Validate that the variant is in range.
        if variant not in range(0, self.variant_count()):
            raise Exception(f"Invalid variant {variant}.")

        # If currently editing a record, update the active variant.
        if self.rid:
            self.data.set_active_variant(self.rid, self.field_id, variant)

        # Update the button.
        self.buttons[variant].setChecked(True)

        for i in range(0, len(self.widgets)):
            if i == variant:
                self.widgets[i].set_target(self.rid)
            else:
                self.widgets[i].set_target(None)

    def variant_count(self):
        return len(self.buttons)
