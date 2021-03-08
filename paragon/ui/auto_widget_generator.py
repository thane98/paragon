from paragon.ui.controllers.auto.union_widget import UnionWidget

from paragon.model.auto_generator_state import AutoGeneratorState
from paragon.model.auto_ui import (
    FormSpec,
    StringLineEditSpec,
    IntSpinBoxSpec,
    HexLineEditSpec,
    CheckBoxSpec,
    ListWidgetSpec,
    MessageWidgetSpec,
    ReferenceWidgetSpec,
    RecordWidgetSpec,
    FloatSpinBoxSpec,
    ScrollSpec,
    UnionWidgetSpec,
)
from paragon.ui.controllers.auto.awakening_support_dialogue_button import (
    AwakeningSupportDialogueButton,
)
from paragon.ui.controllers.auto.bitflags_widget import BitflagsWidget
from paragon.ui.controllers.auto.check_box import CheckBox
from paragon.ui.controllers.auto.collapsible import Collapsible
from paragon.ui.controllers.auto.color_picker import ColorPicker
from paragon.ui.controllers.auto.data_combo_box import DataComboBox
from paragon.ui.controllers.auto.dependent_messages_widget import (
    DependentMessagesWidget,
)
from paragon.ui.controllers.auto.fe14_support_widget import FE14SupportWidget
from paragon.ui.controllers.auto.float_spin_box import FloatSpinBox
from paragon.ui.controllers.auto.form import Form
from paragon.ui.controllers.auto.sprite_form import SpriteForm
from paragon.ui.controllers.auto.fe15_sprite_viewer import FE15SpriteViewer
from paragon.ui.controllers.auto.grid import Grid
from paragon.ui.controllers.auto.group_box import GroupBox
from paragon.ui.controllers.auto.hbox import HBox
from paragon.ui.controllers.auto.hex_line_edit import HexLineEdit
from paragon.ui.controllers.auto.icon_combo_box import IconComboBox
from paragon.ui.controllers.auto.int_spin_box import IntSpinBox
from paragon.ui.controllers.auto.label import Label
from paragon.ui.controllers.auto.labeled_spin_boxes import LabeledSpinBoxes
from paragon.ui.controllers.auto.list_widget import ListWidget
from paragon.ui.controllers.auto.message_widget import MessageWidget
from paragon.ui.controllers.auto.mini_portrait_box import MiniPortraitBox
from paragon.ui.controllers.auto.portrait_viewer import PortraitViewer
from paragon.ui.controllers.auto.read_only_pointer_widget import ReadOnlyPointerWidget
from paragon.ui.controllers.auto.record_widget import RecordWidget
from paragon.ui.controllers.auto.reference_widget import ReferenceWidget
from paragon.ui.controllers.auto.regex_validated_string_line_edit import (
    RegexValidatedStringLineEdit,
)
from paragon.ui.controllers.auto.scroll import Scroll
from paragon.ui.controllers.auto.spin_box_matrix import SpinBoxMatrix
from paragon.ui.controllers.auto.spin_boxes import SpinBoxes
from paragon.ui.controllers.auto.string_line_edit import StringLineEdit
from paragon.ui.controllers.auto.tabs import Tabs
from paragon.ui.controllers.auto.vbox import VBox
from paragon.ui.controllers.auto.widget import Widget


# Long story short: Making widgets aware of multis is more difficult than it sounds.
# To handle this, we create a wrapper for set_target so we can also set multi info.
class MultiSetTargetWrapper:
    def __init__(self, fn, widgets, targets):
        self.fn = fn
        self.widgets = widgets
        self.targets = targets

    def __call__(self, rid, multi_id=None, multi_key=None):
        if multi_id and multi_key:
            for target in self.targets:
                self.widgets[target].update_model_for_multi(multi_id, multi_key)
        self.fn(rid)


class AutoWidgetGenerator:
    def __init__(self, ms, gs):
        self.ms = ms
        self.gs = gs
        self.data = gs.data
        self.specs = gs.specs

        self.defaults = {
            "top_level": ScrollSpec(type="scroll", inner=FormSpec(type="form")),
            "string": StringLineEditSpec(type="string_line_edit"),
            "label": StringLineEditSpec(type="string_line_edit"),
            "int": IntSpinBoxSpec(type="int_spin_box"),
            "float": FloatSpinBoxSpec(type="float_spin_box"),
            "bytes": HexLineEditSpec(type="hex_line_edit"),
            "bool": CheckBoxSpec(type="check_box"),
            "list": ListWidgetSpec(type="list_widget"),
            "message": MessageWidgetSpec(type="message_widget"),
            "reference": ReferenceWidgetSpec(type="reference_widget"),
            "record": RecordWidgetSpec(type="record_widget"),
            "union": UnionWidgetSpec(type="union_widget"),
        }

    def generate_for_type(self, typename, state=None, multi_wrap_ids=None):
        type_metadata = self.data.type_metadata(typename)
        field_metadata = self.data.field_metadata(typename)
        state = AutoGeneratorState(
            main_state=self.ms,
            game_state=self.gs,
            generator=self,
            type_metadata=type_metadata,
            field_metadata=field_metadata,
            typename=typename,
            labeled_widgets=state.labeled_widgets if state else {},
        )
        ui = self.generate_top_level(state, self.get_top_level_spec(typename))
        if size := self.specs.get_dimensions(typename):
            ui.resize(size[0], size[1])
        ui.set_target(None)
        ui.gen_widgets = state.labeled_widgets
        if multi_wrap_ids:
            wrapper = MultiSetTargetWrapper(
                ui.set_target, ui.gen_widgets, multi_wrap_ids
            )
            ui.set_target = wrapper
        return ui

    def generate_top_level(self, state, spec):
        widget = self._generate_top_level(state, spec)
        if spec.widget_id:
            state.labeled_widgets[spec.widget_id] = widget
        return widget

    @staticmethod
    def _generate_top_level(state, spec):
        if spec.type == "form":
            return Form(state, spec)
        elif spec.type == "widget":
            return Widget(state, spec)
        elif spec.type == "group_box":
            return GroupBox(state, spec)
        elif spec.type == "hbox":
            return HBox(state, spec)
        elif spec.type == "vbox":
            return VBox(state, spec)
        elif spec.type == "label":
            return Label(state, spec)
        elif spec.type == "scroll":
            return Scroll(state, spec)
        elif spec.type == "collapsible":
            return Collapsible(state, spec)
        elif spec.type == "grid":
            return Grid(state, spec)
        elif spec.type == "tabs":
            return Tabs(state, spec)
        elif spec.type == "spin_box_matrix":
            return SpinBoxMatrix(state, spec)
        elif spec.type == "portrait_viewer":
            return PortraitViewer(state, spec)
        elif spec.type == "mini_portrait_box":
            return MiniPortraitBox(state, spec)
        elif spec.type == "awakening_support_dialogue_button":
            return AwakeningSupportDialogueButton(state, spec)
        elif spec.type == "fe14_support_widget":
            return FE14SupportWidget(state)
        elif spec.type == "dependent_messages":
            return DependentMessagesWidget(state, spec)
        elif spec.type == "fe15_sprite_viewer":
            return FE15SpriteViewer(state, spec)
        else:
            raise NotImplementedError(f"Unsupported spec {spec.type}")

    def generate(self, state, field_id):
        fm = state.field_metadata[field_id]
        typename = state.typename
        spec = self.get_field_spec(typename, fm["id"], fm["type"])
        widget = self._generate(state, spec, field_id)
        if spec.widget_id:
            state.labeled_widgets[spec.widget_id] = widget
        return widget

    def _generate(self, state, spec, field_id):
        if spec.type == "string_line_edit":
            return StringLineEdit(state, field_id)
        elif spec.type == "regex_validated_string_line_edit":
            return RegexValidatedStringLineEdit(state, spec, field_id)
        elif spec.type == "hex_line_edit":
            return HexLineEdit(state, field_id)
        elif spec.type == "int_spin_box":
            return IntSpinBox(state, spec, field_id)
        elif spec.type == "float_spin_box":
            return FloatSpinBox(state, field_id)
        elif spec.type == "data_combo_box":
            return DataComboBox(state, spec, field_id)
        elif spec.type == "check_box":
            return CheckBox(state, field_id)
        elif spec.type == "list_widget":
            return ListWidget(state, field_id)
        elif spec.type == "reference_widget":
            return ReferenceWidget(state, spec, field_id)
        elif spec.type == "read_only_pointer_widget":
            return ReadOnlyPointerWidget(state, field_id)
        elif spec.type == "message_widget":
            return MessageWidget(state, field_id)
        elif spec.type == "record_widget":
            return RecordWidget(state, spec, field_id)
        elif spec.type == "bitflags_widget":
            return BitflagsWidget(state, spec, field_id)
        elif spec.type == "spin_boxes":
            return SpinBoxes(state, field_id)
        elif spec.type == "labeled_spin_boxes":
            return LabeledSpinBoxes(state, spec, field_id)
        elif spec.type == "color_picker":
            return ColorPicker(state, field_id)
        elif spec.type == "icon_combo_box":
            return IconComboBox(state, spec, field_id)
        elif spec.type == "sprite_form":
            return SpriteForm(state, spec, field_id)
        elif spec.type == "union_widget":
            return UnionWidget(state, field_id)
        else:
            raise NotImplementedError(f"Unsupported spec {spec.type}")

    def get_top_level_spec(self, typename):
        if spec := self.specs.get_top_level_spec(typename):
            return spec
        else:
            return self.defaults["top_level"]

    def get_field_spec(self, typename, field_id, field_type):
        if spec := self.specs.get_field_spec(typename, field_id):
            return spec
        else:
            return self.defaults[field_type]
