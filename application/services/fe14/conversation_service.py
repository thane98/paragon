import json
from typing import List

from PIL import Image, ImageEnhance

from core.loaders.fe14_conversation_assets_loader import FE14ConversationAssetsLoader
from services.service_locator import locator


class ConversationService:
    def __init__(self):
        self.asset_loader = FE14ConversationAssetsLoader()
        self._talk_windows = None
        self._background = None

        with open("Modules/ServiceData/FE14PortraitOverrides.json", "r", encoding="utf-8") as f:
            self._portrait_overrides_english_to_japanese = json.load(f)
            self._portrait_overrides_japanese_to_english = {}
            for key, value in self._portrait_overrides_english_to_japanese.items():
                self._portrait_overrides_japanese_to_english[value] = key
        with open("Modules/ServiceData/FE14EmotionTranslations.json", "r", encoding="utf-8") as f:
            self._emotions_english_to_japanese = json.load(f)
            self._emotions_japanese_to_english = {}
            for key, value in self._emotions_english_to_japanese.items():
                self._emotions_japanese_to_english[value] = key

    @staticmethod
    def fade_image(pillow_image: Image):
        enhancer = ImageEnhance.Brightness(pillow_image)
        return enhancer.enhance(0.3)

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

    def translate_emotions_to_english(self, japanese_emotions: List[str]) -> List[str]:
        result = []
        for emotion in japanese_emotions:
            if emotion in self._emotions_japanese_to_english:
                result.append(self._emotions_japanese_to_english[emotion])
            else:
                result.append(emotion)
        return result

    def translate_emotions_to_japanese(self, english_emotions: List[str]) -> List[str]:
        result = []
        for emotion in english_emotions:
            if emotion in self._emotions_english_to_japanese:
                result.append(self._emotions_english_to_japanese[emotion])
            else:
                result.append(emotion)
        return result

    def translate_speaker_name_to_english(self, speaker_name):
        if speaker_name in self._portrait_overrides_japanese_to_english:
            return self._portrait_overrides_japanese_to_english[speaker_name]
        portrait_data = self.get_portrait_data_for_speaker(speaker_name)
        if not portrait_data["Name"].value:
            return speaker_name
        return portrait_data["Name"].value

    def translate_speaker_name_to_japanese(self, speaker_name):
        if speaker_name in self._portrait_overrides_english_to_japanese:
            return self._portrait_overrides_english_to_japanese[speaker_name]
        portraits = locator.get_scoped("ModuleService").get_module("Portraits / FaceData").entries
        for portrait in portraits:
            if portrait["Name"].value == speaker_name:
                portrait_entry = portrait
                return portrait_entry["FSID"].value[8:]
        return speaker_name

    @staticmethod
    def get_portrait_data_for_speaker(speaker_name):
        fid = "FID_" + speaker_name
        portrait_entry = locator.get_scoped("PortraitService").get_portrait_entry_for_fid(fid, "st")
        if not portrait_entry:
            portrait_entry = locator.get_scoped("PortraitService").get_portrait_entry_for_fid("FID_フードマン", "st")
        return portrait_entry
