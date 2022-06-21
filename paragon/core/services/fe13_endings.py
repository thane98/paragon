import logging

from PySide2 import QtCore
from PySide2.QtGui import QStandardItemModel, QStandardItem

from paragon.core.services.endings import Endings
from paragon.core.textures.texture import Texture
from paragon.model.ending import Ending


class FE13Endings(Endings):
    def _create_model(self) -> QStandardItemModel:
        keys = self.gd.enumerate_messages(self.archive(), True)
        endings = list(
            map(
                lambda k: self.parse_key(k),
                filter(lambda k: k.startswith("MEID_その後_"), keys),
            )
        )
        model = QStandardItemModel()
        for ending in endings:
            item = QStandardItem()
            item.setData(ending, QtCore.Qt.UserRole)
            item.setText(ending.display())
            model.appendRow(item)
        return model

    def _create_ending(self, char1, char2):
        char1_key = self.gd.key(char1) if char1 else None
        char2_key = self.gd.key(char2) if char2 else None
        char1_key = (
            char1_key[4:] if char1_key and char1_key.startswith("PID_") else None
        )
        char2_key = (
            char2_key[4:] if char2_key and char2_key.startswith("PID_") else None
        )
        if char1 and char2:
            key = f"MEID_その後_{char1_key}_{char2_key}"
        elif char1_key:
            key = f"MEID_その後_{char1_key}"
        else:
            raise RuntimeError("Invalid PID found while creating ending!")
        char1_name = self.gd.display(char1) if char1 else None
        char2_name = self.gd.display(char2) if char2 else None
        value = self.gd.message(self.archive(), True, key)
        value = value.replace("\\n", "\n") if value else "Placeholder ending."
        return Ending(key, value, char1, char1_name, char2, char2_name)

    def get_portraits_for_ending(self, ending: Ending):
        if ending.is_single():
            portraits = self.portraits.from_character(ending.char1, "BU")
            if portraits and "通常" in portraits:
                portrait = portraits["通常"]
                return [portrait]
        elif not ending.is_empty():
            portraits = []
            portraits1 = self.portraits.from_character(ending.char1, "FC")
            if portraits1 and "通常" in portraits1:
                portraits.append(portraits1["通常"])
            portraits2 = self.portraits.from_character(ending.char2, "FC")
            if portraits2 and "通常" in portraits2:
                portraits.append(portraits2["通常"])
            return portraits
        return []

    def archive(self):
        return "m/エンディング.bin.lz"

    def _parse_key(self, key, parts):
        value = self.gd.message(self.archive(), True, key)
        if value:
            value = value.replace("\\n", "\n")
        try:
            char1, char1_name = self._extract_character_info(parts[2])
            if len(parts) < 4:
                char2, char2_name = None, None
            else:
                char2, char2_name = self._extract_character_info(parts[3])
            return Ending(key, value, char1, char1_name, char2, char2_name)
        except:
            logging.exception(f"Failed to parse ending key {parts}")
            return Ending(
                key=key,
                value=value,
            )

    def _extract_character_info(self, pid_part):
        pid = "PID_" + pid_part
        char = self.gd.key_to_rid("characters", pid)
        if char:
            return char, self.gd.display(char)
        else:
            return None, None

    def _load_assets(self):
        textures = self.gd.read_ctpk_textures("ui/ending.ctpk.lz")
        window = Texture.from_core_texture(textures["after_window.tga"])
        return {
            "Main": window.crop(0, 0, 400, 240).to_qpixmap(),
            "Double": window.crop(400, 0, 112, 240).to_qpixmap(),
        }
