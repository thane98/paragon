import json
import logging
import os
from typing import List, Tuple, Dict, Optional

from PySide2.QtGui import QPixmap, QFont
from paragon.model.speaker import Speaker

from paragon.model.dialogue_snapshot import DialogueSnapshot

from paragon.core.dialogue.pretty_script_parser import (
    PrettyScriptParser,
    DialogueInterpreterState,
    PauseCommand,
)

from paragon.core.dialogue import convert
from paragon.core.services.portraits import Portraits


class Dialogue:
    def __init__(self, game, config, data, portraits: Portraits, config_root: str):
        self.game = game
        self.config = config
        self.data = data
        self.portraits: Portraits = portraits
        self.loaded_backgrounds = False
        self.background_list = []
        self.loaded_windows = False
        self.window_sets = {}
        self.dialogue_animations = {}

        emotions_path = os.path.join(config_root, "Emotions.json")
        try:
            with open(emotions_path, "r", encoding="utf-8") as f:
                self.emotions = json.load(f)
                self.emotions_reversed = {v: k for k, v in self.emotions.items()}
        except:
            logging.exception("Failed to load dialogue emotion translations.")
            self.emotions = {}
            self.emotions_reversed = {}

        overrides_path = os.path.join(config_root, "PortraitOverrides.json")
        try:
            with open(overrides_path, "r", encoding="utf-8") as f:
                self.overrides = json.load(f)
        except:
            logging.exception("Failed to load portrait overrides.")
            self.overrides = {}

        dialogue_commands_path = "resources/misc/DialogueCommands.json"
        try:
            with open(dialogue_commands_path, "r", encoding="utf-8") as f:
                self.dialogue_commands = json.load(f)
        except:
            logging.exception("Failed to load dialogue commands.")
            self.dialogue_commands = {}

    def render(self, speaker: Speaker, mode: str, active: bool) -> Optional[QPixmap]:
        emotions = speaker.emotions
        name = speaker.fid_alias if speaker.fid_alias else speaker.name
        if speaker.fid_alias:
            fid = speaker.fid_alias
        else:
            asset_translations = self.asset_translations()
            fid = "FID_" + asset_translations.get(name, "")
        emotion_translations = self.emotion_translations()
        real_emotions = []
        for emotion in emotions:
            real_emotions.append(emotion_translations.get(emotion, emotion))
        return self.portraits.render(fid, real_emotions, mode, active)

    def game_to_pretty(self, game_text):
        inverted_emotions = {v: k for k, v in self.emotion_translations().items()}
        inverted_assets = {v: k for k, v in self.asset_translations().items()}
        return convert.game_to_pretty(game_text, inverted_assets, inverted_emotions)

    def pretty_to_game(self, pretty_text):
        emotions = self.emotion_translations()
        assets = self.asset_translations()
        return convert.pretty_to_game(pretty_text, assets, emotions)

    def interpret(self, pretty_text) -> List[DialogueSnapshot]:
        parser = PrettyScriptParser()
        commands = parser.scan(pretty_text)
        state = DialogueInterpreterState(self._get_avatar_config())
        for command in commands:
            command.interpret(state)
        state.commit()
        return state.snapshots

    def backgrounds(self) -> List[Tuple[str, QPixmap]]:
        if not self.loaded_backgrounds:
            try:
                self.background_list = self._load_backgrounds()
            except:
                logging.exception("Failed to load dialogue backgrounds.")
            self.loaded_backgrounds = True
        return self.background_list

    def keys(self) -> List[str]:
        return self.data.enumerate_text_archives()

    def emotion_translations(self) -> Dict[str, str]:
        return self.emotions

    def asset_translations(self) -> Dict[str, str]:
        translations = self._base_asset_translations()
        translations.update(self.overrides)
        return translations

    def windows(self) -> Dict[str, Dict[str, QPixmap]]:
        if not self.loaded_windows:
            try:
                self.window_sets = self._load_windows()
            except:
                logging.exception("Failed to load dialogue windows.")
            self.loaded_windows = True
        return self.window_sets

    def font(self) -> QFont:
        font = QFont("FOT-Chiaro Std B")
        font.setPixelSize(15)
        return font

    def speaker_names(
        self, snapshot: DialogueSnapshot
    ) -> Tuple[Optional[str], Optional[str]]:
        top = snapshot.top_speaker()
        bottom = snapshot.bottom_speaker()
        top_name = self.speaker_name(top) if top else None
        bottom_name = self.speaker_name(bottom) if bottom else None
        return top_name, bottom_name

    def speaker_name(self, speaker: Optional[Speaker]) -> Optional[str]:
        if not speaker:
            return None
        if speaker.name == "":
            return speaker.name
        elif speaker.name == "username":
            config = self._get_avatar_config()
            if config:
                return config.name
            else:
                return None
        elif not speaker.alias:
            asset_translations = self.asset_translations()
            mpid_part = asset_translations.get(speaker.name, speaker.name)
            return self._translate_asset("MPID_" + mpid_part)
        else:
            return self._translate_asset(speaker.alias)

    def _translate_asset(self, alias: str):
        raise NotImplementedError

    def _base_asset_translations(self) -> Dict[str, str]:
        raise NotImplementedError

    def _load_backgrounds(self) -> List[Tuple[str, QPixmap]]:
        raise NotImplementedError

    def _load_windows(self) -> Dict[str, Dict[str, QPixmap]]:
        raise NotImplementedError

    def _get_avatar_config(self):
        raise NotImplementedError
