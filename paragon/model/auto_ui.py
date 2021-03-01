from typing import Literal, Optional, Union, Dict, List

from pydantic import BaseModel


class FormSpec(BaseModel):
    type: Literal["form"]
    ids: Optional[List[str]] = None


class WidgetSpec(BaseModel):
    type: Literal["widget"]
    id: str
    margins: Optional[List[int]] = None


class LabelSpec(BaseModel):
    type: Literal["label"]
    text: str


class SpinBoxMatrixSpec(BaseModel):
    type: Literal["spin_box_matrix"]
    ids: List[str]
    columns: List[str]
    height: int


class GroupBoxSpec(BaseModel):
    type: Literal["group_box"]
    inner: "AnyTopLevelSpec"
    title: Optional[str] = None
    flat: bool = False
    height: Optional[int] = None


class VBoxSpec(BaseModel):
    type: Literal["vbox"]
    inner: List["AnyTopLevelSpec"]
    spacing: int = 5
    spacer: bool = False


class HBoxSpec(BaseModel):
    type: Literal["hbox"]
    inner: List["AnyTopLevelSpec"]
    height: Optional[int] = None
    spacing: int = 5


class ScrollSpec(BaseModel):
    type: Literal["scroll"]
    inner: "AnyTopLevelSpec"


class CollapsibleSpec(BaseModel):
    type: Literal["collapsible"]
    inner: "AnyTopLevelSpec"


class TabSpec(BaseModel):
    title: str
    inner: "AnyTopLevelSpec"


class TabsSpec(BaseModel):
    type: Literal["tabs"]
    tabs: List[TabSpec]


class GridCellSpec(BaseModel):
    inner: "AnyTopLevelSpec"
    row: int = 0
    column: int = 0
    row_span: int = 1
    column_span: int = 1
    no_stretch: bool = False


class GridSpec(BaseModel):
    type: Literal["grid"]
    cells: List[GridCellSpec]


class PortraitViewerSpec(BaseModel):
    type: Literal["portrait_viewer"]
    retrieve_mode: Literal["character", "class", "face_data"]


class MiniPortraitBoxSpec(BaseModel):
    type: Literal["mini_portrait_box"]
    retrieve_mode: Literal["character", "class"]
    mode: str
    image_dim: int = 128
    box_dim: int = 140
    x_transform: int = 0
    y_transform: int = 0


class AwakeningSupportDialogueButtonSpec(BaseModel):
    type: Literal["awakening_support_dialogue_button"]
    field_id: str


class FE14SupportWidgetSpec(BaseModel):
    type: Literal["fe14_support_widget"]


class DependentMessagesEntrySpec(BaseModel):
    path: str
    localized: bool
    key: str
    label: str
    param_count: int
    multiline: bool = False


class DependentMessagesWidgetSpec(BaseModel):
    type: Literal["dependent_messages"]
    key_prefix: str
    lines: List[DependentMessagesEntrySpec]


class UISpec(BaseModel):
    top_level: Optional["AnyTopLevelSpec"] = None
    typename: str
    width: Optional[int] = None
    height: Optional[int] = None
    overrides: Dict[str, "AnyFieldSpec"] = {}


class StringLineEditSpec(BaseModel):
    type: Literal["string_line_edit"]


class HexLineEditSpec(BaseModel):
    type: Literal["hex_line_edit"]


class IntSpinBoxSpec(BaseModel):
    type: Literal["int_spin_box"]
    hex: bool = False


class FloatSpinBoxSpec(BaseModel):
    type: Literal["float_spin_box"]


class DataComboBoxSpec(BaseModel):
    type: Literal["data_combo_box"]
    enum: Optional[str] = None
    items: Optional[Dict] = None
    target_type: Literal["int", "float", "string"] = "int"


class CheckBoxSpec(BaseModel):
    type: Literal["check_box"]


class MessageWidgetSpec(BaseModel):
    type: Literal["message_widget"]


class ReferenceWidgetSpec(BaseModel):
    type: Literal["reference_widget"]
    width: Optional[int] = None


class ReadOnlyPointerWidgetSpec(BaseModel):
    type: Literal["read_only_pointer_widget"]


class RecordWidgetSpec(BaseModel):
    type: Literal["record_widget"]
    read_only: bool = False


class ListWidgetSpec(BaseModel):
    type: Literal["list_widget"]


class BitflagsSpec(BaseModel):
    type: Literal["bitflags_widget"]
    flags: List[str]


class ColorPickerSpec(BaseModel):
    type: Literal["color_picker"]


class SpinBoxesSpec(BaseModel):
    type: Literal["spin_boxes"]


class LabeledSpinBoxesSpec(BaseModel):
    type: Literal["labeled_spin_boxes"]
    labels: List[str]


class IconComboBoxSpec(BaseModel):
    type: Literal["icon_combo_box"]
    icons: str


def update_forward_refs():
    UISpec.update_forward_refs()
    FormSpec.update_forward_refs()
    WidgetSpec.update_forward_refs()
    LabelSpec.update_forward_refs()
    VBoxSpec.update_forward_refs()
    HBoxSpec.update_forward_refs()
    GroupBoxSpec.update_forward_refs()
    ScrollSpec.update_forward_refs()
    CollapsibleSpec.update_forward_refs()
    TabsSpec.update_forward_refs()
    TabSpec.update_forward_refs()
    GridCellSpec.update_forward_refs()
    GridSpec.update_forward_refs()


AnyTopLevelSpec = Union[
    FormSpec,
    WidgetSpec,
    LabelSpec,
    VBoxSpec,
    HBoxSpec,
    GroupBoxSpec,
    ScrollSpec,
    CollapsibleSpec,
    TabsSpec,
    GridSpec,
    SpinBoxMatrixSpec,
    PortraitViewerSpec,
    MiniPortraitBoxSpec,
    AwakeningSupportDialogueButtonSpec,
    FE14SupportWidgetSpec,
    DependentMessagesWidgetSpec,
]

AnyFieldSpec = Union[
    StringLineEditSpec,
    IntSpinBoxSpec,
    HexLineEditSpec,
    DataComboBoxSpec,
    FloatSpinBoxSpec,
    CheckBoxSpec,
    ListWidgetSpec,
    ReferenceWidgetSpec,
    ReadOnlyPointerWidgetSpec,
    MessageWidgetSpec,
    BitflagsSpec,
    SpinBoxesSpec,
    LabeledSpinBoxesSpec,
    ColorPickerSpec,
    RecordWidgetSpec,
    IconComboBoxSpec,
]
