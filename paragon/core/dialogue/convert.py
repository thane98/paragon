from typing import List

from paragon.core.dialogue.pretty_script_parser import PrettyScriptParser

from paragon.core.dialogue.commands import (
    Command,
    NewlineCommand,
    SetSpeakerCommand,
    LoadAssetsCommand,
    SetEmotionsCommand,
)
from paragon.core.dialogue.game_script_parser import GameScriptParser


def translate(commands: List[Command], assets=None, emotions=None):
    if not assets and not emotions:
        return
    for command in commands:
        if assets and isinstance(command, LoadAssetsCommand):
            command.assets = assets.get(command.assets, command.assets)
        elif assets and isinstance(command, SetSpeakerCommand):
            command.speaker = assets.get(command.speaker, command.speaker)
        elif emotions and isinstance(command, SetEmotionsCommand):
            new_emotions = []
            for emotion in command.emotions:
                emotion = emotions.get(emotion, emotion)
                new_emotions.append(emotion)
            command.emotions = new_emotions


def game_to_pretty(game_text: str, assets=None, emotions=None):
    parser = GameScriptParser()
    commands = parser.scan(game_text)
    translate(commands, assets, emotions)
    lines = []
    prev_is_print = False
    for command in commands:
        if isinstance(command, NewlineCommand):
            lines.append(command.to_pretty())
            lines.append("\n")
        elif command.is_print():
            prev_is_print = True
            lines.append(command.to_pretty())
        else:
            if prev_is_print:
                lines.append("\n")
            lines.append(command.to_pretty())
            lines.append("\n")
            if prev_is_print:
                lines.append("\n")
                prev_is_print = False
    return "".join(lines)


def pretty_to_game(pretty_text: str, assets=None, emotions=None) -> str:
    parser = PrettyScriptParser()
    commands = parser.scan(pretty_text)
    translate(commands, assets, emotions)
    return "".join(map(lambda c: c.to_game(), commands))
