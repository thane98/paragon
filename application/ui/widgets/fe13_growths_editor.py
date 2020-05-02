from PySide2.QtWidgets import QLineEdit, QGroupBox, QFormLayout, QSpinBox, QLabel
from .property_widget import PropertyWidget
from .stats_editor import EDITOR_LABELS

_ENC_TABLE = [
    89, 137, 210, 209, 222, 198, 71, 33, 186, 219, 197, 236, 53, 189, 159, 155, 45, 123, 178,
    9, 247, 83, 153, 143, 196, 144, 250, 52, 248, 25, 148, 2, 237, 86, 64, 108, 244, 136, 79, 43,
    180, 187, 235, 116, 183, 13, 194, 164, 238, 147, 207, 66, 241, 23, 191, 240, 165, 188, 15,
    110, 27, 115, 141, 166, 59, 80, 51, 224, 175, 157, 221, 255, 254, 170, 206, 18, 98, 226, 251,
    193, 35, 73, 214, 205, 4, 47, 65, 21, 26, 50, 3, 138, 20, 88, 10, 163, 208, 113, 125, 211, 160,
    82, 190, 215, 139, 72, 55, 19, 168, 68, 8, 60, 227, 99, 246, 223, 22, 124, 70, 243, 7, 204,
    121, 195, 107, 63, 129, 0, 32, 40, 174, 239, 109, 142, 14, 29, 75, 149, 161, 182, 212, 199,
    62, 229, 216, 90, 67, 38, 122, 228, 78, 156, 48, 76, 200, 151, 253, 84, 104, 192, 252, 54,
    28, 117, 1, 150, 233, 31, 69, 6, 112, 44, 41, 103, 46, 245, 158, 146, 96, 61, 232, 231, 102,
    42, 145, 234, 87, 169, 30, 95, 39, 81, 201, 101, 24, 171, 131, 213, 133, 97, 12, 119, 126,
    249, 127, 94, 220, 132, 92, 106, 57, 77, 135, 91, 218, 105, 230, 93, 17, 130, 16, 85, 217,
    203, 140, 114, 134, 111, 100, 128, 202, 162, 5, 172, 74, 177, 11, 56, 225, 173, 49, 179, 152,
    120, 184, 34, 118, 154, 36, 167, 37, 181, 242, 185, 176, 58
]
_LENGTH = 8


def _make_decode_encode_pair(a, b, c, d):
    return [
        lambda j, k, n: _ENC_TABLE[n - (a * ((j ^ b) - c * k) ^ d) & 0xFF],
        lambda j, k, n: _ENC_TABLE.index(n) + (a * ((j ^ b) - c * k) ^ d) & 0xFF
    ]


_CHAR_PAIR = _make_decode_encode_pair(99, 167, 33, 217)
_CLASS_PAIR = _make_decode_encode_pair(35, 70, 241, 120)
_DECODE_PAIR = [_CHAR_PAIR[0], _CLASS_PAIR[0]]
_ENCODE_PAIR = [_CHAR_PAIR[1], _CLASS_PAIR[1]]


# Modified version of https://azalea.qyu.be/2020/157/
# Original growth encryption/decryption documentation can be found here:
# https://forums.serenesforest.net/index.php?/topic/70225-fire-emblem-awakening-growth-rate-cipher-documentation/
class FE13GrowthsEditor(QGroupBox, PropertyWidget):
    def __init__(self, target_property_name: str, mode: int):
        QGroupBox.__init__(self)
        PropertyWidget.__init__(self, target_property_name)
        self.mode = mode
        layout = QFormLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.editors = [
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox()
        ]

        for i in range(0, 8):
            editor = self.editors[i]
            editor.setRange(-128, 127)
            layout.addRow(QLabel(EDITOR_LABELS[i]), editor)
            self.setLayout(layout)

        self.editors[0].valueChanged.connect(lambda: self._on_edit(0, self.editors[0].value()))
        self.editors[1].valueChanged.connect(lambda: self._on_edit(1, self.editors[1].value()))
        self.editors[2].valueChanged.connect(lambda: self._on_edit(2, self.editors[2].value()))
        self.editors[3].valueChanged.connect(lambda: self._on_edit(3, self.editors[3].value()))
        self.editors[4].valueChanged.connect(lambda: self._on_edit(4, self.editors[4].value()))
        self.editors[5].valueChanged.connect(lambda: self._on_edit(5, self.editors[5].value()))
        self.editors[6].valueChanged.connect(lambda: self._on_edit(6, self.editors[6].value()))
        self.editors[7].valueChanged.connect(lambda: self._on_edit(7, self.editors[7].value()))

    def _on_edit(self, index, new_value):
        values = []
        for i, editor in enumerate(self.editors):
            if i == index:
                values.append(new_value)
            else:
                values.append(editor.value())
        encrypted_growths = self._handle_encode_decode(values, _ENCODE_PAIR)
        self.commit(encrypted_growths)

    def _on_target_changed(self):
        if self.target:
            decrypted_growths = self._handle_encode_decode(self._get_target_value(), _DECODE_PAIR)
            for i in range(0, len(self.editors)):
                self.editors[i].setValue(decrypted_growths[i])
        else:
            for editor in self.editors:
                editor.setValue(0)

    def _handle_encode_decode(self, values, pair):
        module = self.target.owner
        if not module:
            raise Exception
        result = []
        table_index = module.entries.index(self.target)
        for index, value in enumerate(values):
            result.append(pair[self.mode](table_index, index, value))
        return result
