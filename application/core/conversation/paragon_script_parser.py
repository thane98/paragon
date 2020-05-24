from typing import Optional, List

from model.conversation.command import Command, PlayerMentionedCommand, SetConversationTypeCommand, \
    RepositionSpeakerCommand, LoadPortraitsCommand, PlayVoiceCommand, PlaySoundEffectCommand, PlayMusicCommand, \
    StopMusicCommand, SetSpeakerAliasCommand, GenderDependentMessageCommand, PrintAvatarNameCommand, PauseCommand, \
    PauseNewlineCommand, ClearMessageCommand, DeleteSpeakerCommand, SetTalkWindowPanickedCommand, \
    SetTalkBoxScrollInCommand, CutsceneActionCommand, WaitCommand, AdjustSoundVolumeCommand, DramaticLineCommand, \
    ConditionalFIDCommand, PlayerMarriageSceneCommand, PlayMusicWithVolumeRampCommand, CancelMusicRampCommand, \
    SetSpeakerCommand, PrintCommand, SetEmotionCommand, PlayMessageCommand, FadeInCommand, FadeOutCommand, \
    FadeWhiteCommand
from model.conversation.source_position import SourcePosition
from model.conversation.transpiler_error import TranspilerError
from services.service_locator import locator


class ParagonScriptParser:
    def __init__(self):
        self._position: int = 0
        self._input: Optional[str] = None
        self._commands: List[Command] = []
        self._line = 1
        self._line_start = 0

        self._command_to_func = {
            "HasPermanents": self._parse_player_mentioned_command,
            "ConversationType": self._parse_set_conversation_type_command,
            "NewSpeaker": self._parse_load_portraits_command,
            "Reposition": self._parse_reposition_speaker_command,
            "SetSpeaker": self._parse_set_speaker_command,
            "Emotions": self._parse_set_emotion_command,
            "PlayVoice": self._parse_play_voice_command,
            "PlaySoundEffect": self._parse_play_sound_effect_command,
            "PlayMusic": self._parse_play_music_command,
            "StopMusic": self._parse_stop_music_command,
            "Alias": self._parse_set_speaker_alias_command,
            "Await": self._parse_pause_command,
            "AwaitAndClear": self._parse_pause_newline_command,
            "Clear": self._parse_clear_message_command,
            "DeleteSpeaker": self._parse_delete_speaker_command,
            "Panicked": self._parse_set_talk_window_panicked_command,
            "Scrolling": self._parse_set_talk_box_scroll_in_command,
            "CutsceneAction": self._parse_cutscene_action_command,
            "Wait": self._parse_wait_command,
            "Volume": self._parse_adjust_sound_volume_command,
            "Dramatic": self._parse_dramatic_line_command,
            "OverridePortrait": self._parse_conditional_fid_command,
            "ShowMarriageScene": self._parse_player_marriage_scene_command,
            "Ramp": self._parse_music_with_volume_ramp_command,
            "StopRamp": self._parse_cancel_music_ramp_command,
            "FadeIn": self._parse_fade_in_command,
            "FadeOut": self._parse_fade_out_command,
            "FadeWhite": self._parse_fade_white_command,
            "Nu": self._parse_print_avatar_name_command,
            "G": self._parse_gender_dependent_alias_command
        }

    def reset(self):
        self._position = 0
        self._line = 1
        self._line_start = 0
        self._input = None
        self._commands = []

    def parse(self, input: str):
        self.reset()
        self._input = input
        while self._position < len(self._input):
            self._skip_whitespace(True)
            if self._peek() == "$":
                self._parse_command()
            else:
                self._parse_text()
            self._skip_whitespace(True)
        return self._commands

    def _parse_text(self):
        current_text = []
        commands = []
        while True:
            if self._peek() == "$":
                if current_text:
                    commands.append(PrintCommand("".join(current_text)))
                    current_text.clear()

                pos = self._position
                self._position += 1
                command = self._scan_alpha()
                if command == "G" or command == "Nu":
                    commands.append(self._command_to_func[command]())
                else:
                    self._position = pos
                    break
            else:
                current_text.append(self._next())
        if current_text:
            commands.append(PrintCommand("".join(current_text).rstrip()))
            current_text.clear()
        self._commands.extend(commands)

    def _scan_alpha(self):
        string = []
        while self._peek().isalpha():
            string.append(self._next())
        return "".join(string)

    def _parse_command(self, skip_whitespace_after_command=True):
        self._expect("$")
        command = self._scan_alpha()
        if skip_whitespace_after_command:
            self._skip_whitespace()
        if command not in self._command_to_func:
            raise TranspilerError(self._source_position(), "Unknown command $" + command)
        command = self._command_to_func[command]()
        if isinstance(command, list):
            self._commands.extend(command)
        else:
            self._commands.append(command)

    def _next(self) -> str:
        if self._position >= len(self._input):
            raise TranspilerError(self._source_position(), "Reached EOF while parsing.")
        result = self._peek()
        if result == "\n":
            self._line += 1
            self._line_start = self._position + 1
        self._position += 1
        return result

    def _safe_lookahead(self, amount: int) -> str:
        if self._position + amount >= len(self._input):
            return ""
        return self._input[self._position + amount]

    def _scan_int(self) -> int:
        result = ""
        while self._peek().isdigit():
            result += self._next()
        return self._convert_string_to_int(result)

    def _convert_string_to_int(self, string: str):
        try:
            return int(string)
        except:
            raise TranspilerError(self._source_position(), "Expected a number.")

    def _expect(self, expected_char: str):
        next_char = self._next()
        if next_char != expected_char:
            raise TranspilerError(self._source_position(), "Expected %s found %s" % (expected_char, next_char))

    def _peek(self) -> str:
        if self._position >= len(self._input):
            return "\0"
        return self._input[self._position]

    def _source_position(self) -> SourcePosition:
        return SourcePosition(self._line, self._position - self._line_start)

    def _skip_whitespace(self, include_newlines=False):
        if include_newlines:
            whitespace = [" ", "\t", "\n", "\r"]
        else:
            whitespace = [" ", "\t"]
        while self._peek() in whitespace:
            self._next()

    def _read_until(self, end_characters: List[str], error_on_eol: bool = True):
        result = []
        while self._peek() not in end_characters:
            if error_on_eol and self._peek() == "\n":
                raise TranspilerError(self._source_position(), "Reached EOL while parsing.")
            result.append(self._next())
        return "".join(result)

    def _parse_args(self, funcs):
        result = []
        self._skip_whitespace()
        self._expect("(")
        for i, func in enumerate(funcs):
            self._skip_whitespace()
            arg = func()
            result.append(arg)
            if i != len(funcs) - 1:
                self._skip_whitespace()
                self._expect(",")
        self._skip_whitespace()
        self._expect(")")
        return result

    def _scan_string_arg(self) -> str:
        result = self._read_until([",", ")"])
        return result

    def _parse_player_mentioned_command(self):
        return PlayerMentionedCommand()

    def _parse_set_conversation_type_command(self):
        string = self._read_until(["\r", "\n"]).strip()
        return SetConversationTypeCommand(self._convert_string_to_int(string))

    def _parse_load_portraits_command(self):
        speaker = self._read_until(["\r", "\n", " ", "\t", "\0"]).strip()
        translated = locator.get_scoped("ConversationService").translate_speaker_name_to_japanese(speaker)
        return LoadPortraitsCommand(translated)

    def _parse_reposition_speaker_command(self):
        string = self._read_until(["\r", "\n", "\0"]).strip()
        return RepositionSpeakerCommand(self._convert_string_to_int(string))

    def _parse_set_speaker_command(self):
        speaker = self._read_until(["\r", "\n", "\0"]).strip()
        translated = locator.get_scoped("ConversationService").translate_speaker_name_to_japanese(speaker)
        return SetSpeakerCommand(translated)

    def _parse_set_emotion_command(self):
        self._skip_whitespace()
        self._expect("(")
        emotions = self._read_until([")"]).split(",")
        translated = locator.get_scoped("ConversationService").translate_emotions_to_japanese(emotions)
        self._expect(")")
        return SetEmotionCommand(translated)

    def _parse_play_voice_command(self):
        voice_line = self._read_until(["\r", "\n", "\0"]).strip()
        return PlayVoiceCommand(voice_line)

    def _parse_play_sound_effect_command(self):
        effect_name = self._read_until(["\r", "\n", "\0"]).strip()
        return PlaySoundEffectCommand(effect_name)

    def _parse_play_music_command(self):
        args = self._parse_args([self._scan_string_arg, self._scan_int])
        return PlayMusicCommand(args[0], args[1])

    def _parse_stop_music_command(self):
        string = self._read_until(["\r", "\n", "\0"]).strip()
        return StopMusicCommand(self._convert_string_to_int(string))

    def _parse_set_speaker_alias_command(self):
        mpid = self._read_until(["\r", "\n", "\0"]).strip()
        return SetSpeakerAliasCommand(mpid)

    def _parse_gender_dependent_alias_command(self):
        args = self._parse_args([self._scan_string_arg, self._scan_string_arg])
        return GenderDependentMessageCommand(args[0], args[1])

    def _parse_print_avatar_name_command(self):
        return PrintAvatarNameCommand()

    def _parse_pause_command(self):
        return [PlayMessageCommand(), PauseCommand()]

    def _parse_pause_newline_command(self):
        return [PlayMessageCommand(), PauseNewlineCommand()]

    def _parse_clear_message_command(self):
        return ClearMessageCommand()

    def _parse_delete_speaker_command(self):
        return DeleteSpeakerCommand()

    def _parse_set_talk_window_panicked_command(self):
        return SetTalkWindowPanickedCommand()

    def _parse_set_talk_box_scroll_in_command(self):
        return SetTalkBoxScrollInCommand()

    def _parse_cutscene_action_command(self):
        string = self._read_until(["\r", "\n", "\0"]).strip()
        return CutsceneActionCommand(string)

    def _parse_wait_command(self):
        string = self._read_until(["\r", "\n"]).strip()
        return WaitCommand(self._convert_string_to_int(string))

    def _parse_adjust_sound_volume_command(self):
        args = self._parse_args([self._scan_int, self._scan_int])
        return AdjustSoundVolumeCommand(args[0], args[1])

    def _parse_dramatic_line_command(self):
        string = self._read_until(["\r", "\n", "\0"]).strip()
        return DramaticLineCommand(self._convert_string_to_int(string))

    def _parse_conditional_fid_command(self):
        param = self._read_until(["\r", "\n", "\0"]).strip()
        return ConditionalFIDCommand(param)

    def _parse_player_marriage_scene_command(self):
        character = self._read_until(["\r", "\n", "\0"]).strip()
        return PlayerMarriageSceneCommand(character)

    def _parse_music_with_volume_ramp_command(self):
        args = self._parse_args([self._scan_string_arg, self._scan_int])
        return PlayMusicWithVolumeRampCommand(args[0], args[1])

    def _parse_cancel_music_ramp_command(self):
        args = self._parse_args([self._scan_string_arg, self._scan_int])
        return CancelMusicRampCommand(args[0], args[1])

    def _parse_fade_in_command(self):
        string = self._read_until(["\r", "\n", "\0"]).strip()
        return FadeInCommand(self._convert_string_to_int(string))

    def _parse_fade_out_command(self):
        string = self._read_until(["\r", "\n", "\0"]).strip()
        return FadeOutCommand(self._convert_string_to_int(string))

    def _parse_fade_white_command(self):
        string = self._read_until(["\r", "\n", "\0"]).strip()
        return FadeWhiteCommand(self._convert_string_to_int(string))
