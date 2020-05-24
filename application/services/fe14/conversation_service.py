import io
from typing import List

from PIL import Image, ImageEnhance
from PySide2.QtCore import QBuffer
from PySide2.QtGui import QPixmap

from core.loaders.fe14_conversation_assets_loader import FE14ConversationAssetsLoader
from services.service_locator import locator


_EMOTIONS_JAPANESE_TO_ENGLISH = {
    "汗": "Sweat",
    "照": "Blush",
    "通常": "Standard",
    "びっくり": "Surprised",
    "怒": "Angry",
    "苦": "Suffering",
    "笑": "Laughing",
    "キメ": "Great",
    "やけくそ": "Desperate",
    "囚": "Possessed"
}

_EMOTIONS_ENGLISH_TO_JAPANESE = {
    "Sweat": "汗",
    "Blush": "照",
    "Standard": "通常",
    "Surprised": "びっくり",
    "Angry": "怒",
    "Suffering": "苦",
    "Laughing": "笑",
    "Great": "キメ",
    "Desperate": "やけくそ",
    "Possessed": "囚"
}


class ConversationService:
    def __init__(self):
        self.asset_loader = FE14ConversationAssetsLoader()
        self._talk_windows = None
        self._background = None

    @staticmethod
    def fade_pixmap(image: QPixmap):
        buffer = QBuffer()
        buffer.open(QBuffer.ReadWrite)
        image.save(buffer, "PNG")

        pillow_image = Image.open(io.BytesIO(buffer.data()))
        enhancer = ImageEnhance.Brightness(pillow_image)
        return QPixmap.fromImage(enhancer.enhance(0.3).toqimage())

    def talk_windows(self):
        if not self._talk_windows:
            self._talk_windows = self.asset_loader.load_talk_windows()
        return self._talk_windows

    def background(self):
        if not self._background:
            self._background = self.asset_loader.load_background()
        return self._background

    def set_avatar_name(self, name: str):
        project = locator.get_scoped("Driver").get_project()
        if project.metadata:
            project.metadata["AvatarName"] = name
        else:
            project.metadata = {"AvatarName": name}

    def get_avatar_name(self):
        project = locator.get_scoped("Driver").get_project()
        if project.metadata:
            return project.metadata.get("AvatarName", "Corrin")
        else:
            return "Corrin"

    def set_avatar_is_female(self, is_female: bool):
        project = locator.get_scoped("Driver").get_project()
        if project.metadata:
            project.metadata["AvatarIsFemale"] = is_female
        else:
            project.metadata = {"AvatarIsFemale": is_female}

    def avatar_is_female(self):
        project = locator.get_scoped("Driver").get_project()
        if project.metadata:
            return project.metadata.get("AvatarIsFemale", True)
        else:
            return True

    def get_portraits_for_fid(self, fid: str, mode: str = "st"):
        portrait_service = locator.get_scoped("PortraitService")
        if fid == "FID_username":
            portraits = locator.get_scoped("PortraitService").get_avatar_portraits(self.avatar_is_female())
        else:
            portraits = portrait_service.get_portraits_for_fid(fid, mode)
            if not portraits:
                portraits = portrait_service.get_portraits_for_fid("FID_フードマン", mode)
        return portraits

    def get_blush_and_sweat_coordinates(self, fid: str, mode: str):
        if fid == "FID_username":
            if self.avatar_is_female():
                fid = "FID_マイユニ_女2_顔A"
            else:
                fid = "FID_マイユニ_男1_顔B"
        return locator.get_scoped("PortraitService").get_blush_and_sweat_coordinates(fid, mode)

    def get_display_name(self, fid: str):
        if fid == "FID_username":
            return self.get_avatar_name()
        else:
            portrait_entry = locator.get_scoped("PortraitService").get_portrait_entry_for_fid(fid, "st")
            if not portrait_entry:
                portrait_entry = locator.get_scoped("PortraitService").get_portrait_entry_for_fid("FID_フードマン", "st")
        return portrait_entry["Name"].value

    @staticmethod
    def translate_emotions_to_english(japanese_emotions: List[str]) -> List[str]:
        result = []
        for emotion in japanese_emotions:
            if emotion in _EMOTIONS_JAPANESE_TO_ENGLISH:
                result.append(_EMOTIONS_JAPANESE_TO_ENGLISH[emotion])
            else:
                result.append(emotion)
        return result

    @staticmethod
    def translate_emotions_to_japanese(english_emotions: List[str]) -> List[str]:
        result = []
        for emotion in english_emotions:
            if emotion in _EMOTIONS_ENGLISH_TO_JAPANESE:
                result.append(_EMOTIONS_ENGLISH_TO_JAPANESE[emotion])
            else:
                result.append(emotion)
        return result

    def translate_speaker_name_to_english(self, speaker_name):
        if speaker_name == "username":
            return "username"
        portrait_data = self.get_portrait_data_for_speaker(speaker_name)
        return portrait_data["Name"].value

    @staticmethod
    def translate_speaker_name_to_japanese(speaker_name):
        if speaker_name == "username":
            return "username"
        portrait_entry = locator.get_scoped("PortraitService").get_portrait_entry_for_fid("FID_フードマン", "st")
        portraits = locator.get_scoped("ModuleService").get_module("Portraits / FaceData").entries
        for portrait in portraits:
            if portrait["Name"].value == speaker_name:
                portrait_entry = portrait
                break
        return portrait_entry["FSID"].value[8:]

    @staticmethod
    def get_portrait_data_for_speaker(speaker_name):
        fid = "FID_" + speaker_name
        portrait_entry = locator.get_scoped("PortraitService").get_portrait_entry_for_fid(fid, "st")
        if not portrait_entry:
            portrait_entry = locator.get_scoped("PortraitService").get_portrait_entry_for_fid("FID_フードマン", "st")
        return portrait_entry
