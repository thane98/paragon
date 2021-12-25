from paragon.core.dialogue.commands import (
    SetConversationTypeCommand,
    LoadAssetsCommand,
    WaitCommand,
    SetSpeakerCommand,
    SynchronizeCommand,
    PrintCommand,
    PauseCommand,
    NewlineCommand,
    ClearCommand,
)

from paragon.core.scanner import ScannerError


def parse(dialogue: str, char1: str, char1_pos: int, char2: str, char2_pos: int):
    commands = [
        SetConversationTypeCommand(1),
        LoadAssetsCommand(_get_speaker(char1), char1_pos),
        LoadAssetsCommand(_get_speaker(char2), char2_pos),
        WaitCommand(0),
    ]
    speaker = None
    lines = dialogue.splitlines()
    for i, line in enumerate(lines):
        if stripped := line.strip():
            if stripped.startswith(char1 + ":"):
                current_char = char1
            elif stripped.startswith(char2 + ":"):
                current_char = char2
            else:
                raise ScannerError(
                    stripped, i, "Line must start with a character name followed by ':'"
                )
            parts = stripped.split(":", 1)
            new_speaker, new_text = current_char, parts[1].strip()

            # If this isn't the first line, figure out how to clear the previous text.
            if speaker and new_speaker != speaker:
                commands.append(NewlineCommand())
            elif speaker and new_speaker == speaker:
                commands.append(ClearCommand())

            # Switch speakers if necessary.
            if new_speaker != speaker:
                commands.extend(
                    [
                        SetSpeakerCommand(_get_speaker(parts[0])),
                        SynchronizeCommand(),
                    ]
                )

            # Print the text.
            commands.extend(
                [
                    PrintCommand(new_text),
                    PauseCommand(),
                ]
            )

            speaker = new_speaker
    return commands


def _get_speaker(speaker_part):
    if speaker_part == "Corrin":
        return "username"
    else:
        return speaker_part
