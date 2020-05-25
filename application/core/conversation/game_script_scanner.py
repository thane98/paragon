from typing import Optional

from model.conversation.command import *
from model.conversation.source_position import SourcePosition
from model.conversation.transpiler_error import TranspilerError


# TODO: Support argument commands like $a0 and $a1
class GameScriptScanner:
    def __init__(self):
        self._position = 0
        self._tokens: List[Command] = []
        self._input: Optional[str] = None

        self._three_char_commands = {
            "Svp": self._scan_play_voice_command,
            "Ssp": self._scan_play_sound_effect_command,
            "Sbp": self._scan_play_music_command,
            "Sbs": self._scan_stop_music_command,
            "Sbv": self._scan_adjust_sound_volume_command,
            "Sre": self._scan_dramatic_line_command,
            "Srp": self._scan_dramatic_music_command,
            "Slp": self._scan_player_music_with_volume_ramp_command,
            "Sls": self._scan_cancel_music_ramp_command,
            "Slv": self._scan_set_ramp_volume_command
        }
        self._two_char_commands = {
            "Wm": self._scan_load_portraits_command,
            "Ws": self._scan_set_speaker_command,
            "VN": self._scan_set_speaker_alias_command,
            "VF": self._scan_conditional_fid_command,
            "Nu": self._scan_print_avatar_name_command,
            "Wc": self._scan_set_talk_box_scroll_in_command,
            "Wd": self._scan_delete_speaker_command,
            "Wa": self._scan_synchronize_command,
            "Wv": self._scan_set_talk_window_panicked_command,
            "Fi": self._scan_fade_in_command,
            "Fo": self._scan_fade_out_command,
            "Fw": self._scan_fade_white_command,
            "Tc": self._scan_visual_effect_command,
            "k\n": self._scan_pause_newline_command
        }
        self._one_char_commands = {
            "a": self._scan_player_mentioned_command,
            "c": self._scan_color_command,
            "t": self._scan_set_conversation_type_command,
            "E": self._scan_set_emotion_command,
            "G": self._scan_gender_dependent_message_command,
            "k": self._scan_pause_command,
            "p": self._scan_clear_message_command,
            "b": self._scan_cutscene_action_command,
            "w": self._scan_wait_command,
            "l": self._scan_player_marriage_scene_command
        }

    def reset(self):
        self._position = 0
        self._tokens = []
        self._input = None

    def scan(self, input) -> List[Command]:
        self.reset()
        self._input = input
        while self._position < len(self._input):
            if self._peek() == "|":
                self._position += 1
            else:
                next_token = self._next_token()
                if not next_token:
                    break
                else:
                    self._tokens.extend(next_token)
        return self._tokens

    def _next_token(self) -> Optional[List[Command]]:
        next_char = self._peek()
        if next_char == "\0":
            return None
        elif next_char == "$":
            command = self._scan_command()
            if self._requires_forced_newline(command):
                result = [PlayMessageCommand(), ForcedNewlineCommand()]
                result.extend(command)
                return result
            return command
        elif next_char.isdigit():
            return [RepositionSpeakerCommand(self._scan_int())]
        else:
            return [PrintCommand(self._scan_string())]

    def _requires_forced_newline(self, scanned_commands):
        if not self._tokens or not isinstance(self._tokens[-1], PrintCommand):
            return False
        if not scanned_commands:
            return False
        if isinstance(scanned_commands[0], (PrintAvatarNameCommand, ArgumentCommand, GenderDependentMessageCommand)):
            return False
        return not isinstance(scanned_commands[0], PlayMessageCommand)

    def _scan_command(self) -> List[Command]:
        self._next()  # Consume the dollar sign.
        three_char_command = self._peek() + self._safe_lookahead(1) + self._safe_lookahead(2)
        two_char_command = self._peek() + self._safe_lookahead(1)
        one_char_command = self._peek()
        if three_char_command in self._three_char_commands:
            self._position += 3
            return self._three_char_commands[three_char_command]()
        elif two_char_command in self._two_char_commands:
            self._position += 2
            return self._two_char_commands[two_char_command]()
        elif one_char_command in self._one_char_commands:
            self._position += 1
            return self._one_char_commands[one_char_command]()
        else:
            raise TranspilerError(self._source_position(), "Unrecognized command " + self._input[self._position:])

    def _scan_int(self) -> int:
        result = ""
        while self._peek().isdigit():
            result += self._next()
        return int(result)

    def _scan_string(self):
        result = ""
        next_char = self._peek()
        while next_char != "|" and next_char != "$" and next_char != "\0":
            result += self._next()
            next_char = self._peek()
        return result

    def _next(self) -> str:
        if self._position >= len(self._input):
            raise TranspilerError(self._source_position(), "Reached EOL while parsing.")
        result = self._peek()
        self._position += 1
        return result

    def _expect(self, expected_char: str):
        next_char = self._next()
        if next_char != expected_char:
            raise TranspilerError(self._source_position(), "Expected %s found %s" % (expected_char, next_char))

    def _peek(self) -> str:
        if self._position >= len(self._input):
            return "\0"
        return self._input[self._position]

    def _safe_lookahead(self, amount: int) -> str:
        if self._position + amount >= len(self._input):
            return ""
        return self._input[self._position + amount]

    def _source_position(self) -> SourcePosition:
        return SourcePosition(1, self._position)

    def _scan_player_mentioned_command(self):
        if self._peek().isdigit():
            return [ArgumentCommand(self._scan_int())]
        return [PlayerMentionedCommand()]

    def _scan_set_conversation_type_command(self):
        return [SetConversationTypeCommand(self._scan_int())]

    def _scan_load_portraits_command(self):
        return [LoadPortraitsCommand(self._scan_string())]

    def _scan_set_speaker_command(self):
        return [SetSpeakerCommand(self._scan_string())]

    def _scan_set_emotion_command(self):
        return [SetEmotionCommand(self._scan_string().split(","))]

    def _scan_play_voice_command(self):
        return [PlayVoiceCommand(self._scan_string())]

    def _scan_play_sound_effect_command(self):
        return [PlaySoundEffectCommand(self._scan_string())]

    def _scan_play_music_command(self):
        music = self._scan_string()
        self._expect("|")
        delay = self._scan_int()
        return [PlayMusicCommand(music, delay)]

    def _scan_stop_music_command(self):
        return [StopMusicCommand(self._scan_int())]

    def _scan_set_speaker_alias_command(self):
        return [SetSpeakerAliasCommand(self._scan_string())]

    def _scan_gender_dependent_message_command(self):
        messages = self._scan_string().split(",")
        if len(messages) < 2:
            raise TranspilerError(self._source_position(), "Invalid $G command.")
        return [GenderDependentMessageCommand(messages[0], messages[1])]

    def _scan_print_avatar_name_command(self):
        return [PrintAvatarNameCommand()]

    def _scan_pause_command(self):
        return [PlayMessageCommand(), PauseCommand()]

    def _scan_pause_newline_command(self):
        return [PlayMessageCommand(), PauseNewlineCommand()]

    def _scan_clear_message_command(self):
        return [ClearMessageCommand()]

    def _scan_delete_speaker_command(self):
        return [DeleteSpeakerCommand()]

    def _scan_synchronize_command(self):
        return [SynchronizeCommand()]

    def _scan_set_talk_window_panicked_command(self):
        return [SetTalkWindowPanickedCommand()]

    def _scan_set_talk_box_scroll_in_command(self):
        return [SetTalkBoxScrollInCommand()]

    def _scan_cutscene_action_command(self):
        result = []
        while self._peek() != ";" and self._peek() != "|":
            result.append(self._next())
        if self._peek() == ";":
            result.append(self._next())
        else:
            self._position += 1  # Skip the delimiter.
        return [CutsceneActionCommand("".join(result))]

    def _scan_wait_command(self):
        return [WaitCommand(self._scan_int())]

    def _scan_adjust_sound_volume_command(self):
        new_volume = self._scan_int()
        self._expect("|")
        delay = self._scan_int()
        return [AdjustSoundVolumeCommand(new_volume, delay)]

    def _scan_dramatic_line_command(self):
        return [DramaticLineCommand(self._scan_int())]

    def _scan_dramatic_music_command(self):
        music = self._scan_string()
        self._expect("|")
        volume = self._scan_int()
        return [DramaticMusicCommand(music, volume)]

    def _scan_conditional_fid_command(self):
        return [ConditionalFIDCommand(self._scan_string())]

    def _scan_player_marriage_scene_command(self):
        return [PlayerMarriageSceneCommand(self._scan_string())]

    def _scan_player_music_with_volume_ramp_command(self):
        music = self._scan_string()
        self._expect("|")
        ramp_time = self._scan_int()
        return [PlayMusicWithVolumeRampCommand(music, ramp_time)]

    def _scan_cancel_music_ramp_command(self):
        music = self._scan_string()
        self._expect("|")
        delay = self._scan_int()
        return [CancelMusicRampCommand(music, delay)]

    def _scan_fade_in_command(self):
        return [FadeInCommand(self._scan_int())]

    def _scan_fade_out_command(self):
        return [FadeOutCommand(self._scan_int())]

    def _scan_fade_white_command(self):
        return [FadeWhiteCommand(self._scan_int())]

    def _scan_color_command(self):
        color_1 = self._scan_int()
        self._expect(",")
        color_2 = self._scan_int()
        self._expect(",")
        color_3 = self._scan_int()
        self._expect(",")
        color_4 = self._scan_int()
        color = [str(color_1), str(color_2), str(color_3), str(color_4)]
        return [ColorCommand(color)]

    def _scan_visual_effect_command(self):
        return [VisualEffectCommand(self._scan_string())]

    def _scan_set_ramp_volume_command(self):
        music = self._scan_string()
        self._expect("|")
        volume = self._scan_int()
        self._expect("|")
        delay = self._scan_int()
        return [SetRampVolumeCommand(music, volume, delay)]
