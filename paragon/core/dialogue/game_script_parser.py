from paragon.core.dialogue.scanner import Scanner
from paragon.core.dialogue.commands import *


class GameScriptParser:
    def __init__(self):
        self.one_char = {
            "a": self._scan_param,
            "Z": self._scan_overworld,
            "c": self._scan_color,
            "t": self._scan_set_conversation_type,
            "E": self._scan_set_emotions,
            "G": self._scan_print_gender_dependent,
            "k": self._scan_pause,
            "p": self._scan_clear,
            "C": self._scan_c,
            "b": self._scan_bev,
            "w": self._scan_wait,
            "l": self._scan_marriage,
        }
        self.two_char = {
            "Wf": self._scan_wf,
            "Tc": self._scan_visual_effect,
            "Td": self._scan_visual_effect_2,
            "Fw": self._scan_fade_white,
            "Fo": self._scan_fade_out,
            "Fi": self._scan_fade_in,
            "Wv": self._scan_set_talk_window_panicked,
            "Wa": self._scan_synchronize,
            "WD": self._scan_delete_speaker,  # Special case for a couple SoV files.
            "Wd": self._scan_delete_speaker,
            "Wc": self._scan_set_talk_window_scroll_in,
            "Nu": self._scan_print_avatar,
            "Np": self._scan_print_avatar_2,
            "Nl": self._scan_print_online_player,
            "VF": self._scan_fid_alias,
            "VN": self._scan_alias,
            "Ws": self._scan_set_speaker,
            "Wm": self._scan_load_assets,
        }
        self.three_char = {
            "Bbs": self._scan_bbs,
            "Bbe": self._scan_bbe,
            "Sev": self._scan_sev,
            "Svp": self._scan_play_voice,
            "Svj": self._scan_play_voice_japanese,
            "Sve": self._scan_play_voice_english,
            "Ssp": self._scan_play_sound_effect,
            "Ssw": self._scan_play_sound_effect_2,
            "Sbp": self._scan_play_music,
            "Sbs": self._scan_stop_music,
            "Sbv": self._scan_set_volume,
            "Sre": self._scan_dramatic_line,
            "Srp": self._scan_dramatic_music,
            "Slp": self._scan_play_ramp,
            "Sls": self._scan_stop_ramp,
            "Slv": self._scan_set_ramp_volume,
        }

    def scan(self, input: str):
        if not input:
            return []
        sc = Scanner(input)
        commands = []
        while not sc.at_end():
            if sc.peek() == "|":
                sc.next()
            if sc.peek() == "$":
                commands.append(self._scan_command(sc))
            elif self._next_is_newline(sc):
                sc.expect("\\")
                sc.expect("n")
                commands.append(NewlineCommand())
            else:
                commands.append(self._scan_print(sc))
        return commands

    def _scan_command(self, sc: Scanner):
        sc.next()  # Skip the dollar sign.
        three = sc.peek() + sc.peek(1) + sc.peek(2)
        two = sc.peek() + sc.peek(1)
        one = sc.peek()
        if three in self.three_char:
            sc.advance(3)
            return self.three_char[three](sc)
        elif two in self.two_char:
            sc.advance(2)
            return self.two_char[two](sc)
        elif one in self.one_char:
            sc.advance(1)
            return self.one_char[one](sc)
        else:
            sc.error("Unrecognized command.")

    @staticmethod
    def _next_is_newline(sc: Scanner) -> bool:
        return sc.peek() == "\\" and sc.peek(1) == "n"

    @staticmethod
    def _scan_param(sc: Scanner) -> Command:
        if sc.peek().isdigit():
            return ParamCommand(sc.scan_number())
        else:
            return PlayerMentionedCommand()

    @staticmethod
    def _scan_overworld(_sc: Scanner) -> Command:
        return OverworldCommand()

    @staticmethod
    def _scan_color(sc: Scanner) -> Command:
        r = sc.scan_number()
        sc.expect(",")
        g = sc.scan_number()
        sc.expect(",")
        b = sc.scan_number()
        sc.expect(",")
        a = sc.scan_number()
        return ColorCommand(r, g, b, a)

    @staticmethod
    def _scan_set_conversation_type(sc: Scanner) -> Command:
        t = sc.scan_number()
        return SetConversationTypeCommand(t)

    @staticmethod
    def _scan_set_emotions(sc: Scanner) -> Command:
        emotions = []
        while sc.peek() != "|":
            if sc.peek() == ",":
                sc.next()
            else:
                emotion = sc.scan_until({",", "|"})
                emotions.append(emotion)
        sc.expect("|")
        return SetEmotionsCommand(emotions)

    @staticmethod
    def _scan_print_gender_dependent(sc: Scanner) -> Command:
        m = sc.scan_until({","})
        sc.expect(",")
        f = sc.scan_until({"|"})
        sc.expect("|")
        return PrintGenderDependentCommand(m, f)

    @staticmethod
    def _scan_pause(_sc: Scanner) -> Command:
        return PauseCommand()

    @staticmethod
    def _scan_clear(_sc: Scanner) -> Command:
        return ClearCommand()

    @staticmethod
    def _scan_wf(_sc: Scanner) -> Command:
        return WfCommand()

    @staticmethod
    def _scan_c(_sc: Scanner) -> Command:
        return CCommand()

    @staticmethod
    def _scan_bbs(sc: Scanner) -> Command:
        a = sc.scan_until({","})
        sc.expect(",")
        b = sc.scan_until({","})
        sc.expect(",")
        c = sc.scan_until({"|"})
        sc.expect("|")
        return BbsCommand(a, b, c)

    @staticmethod
    def _scan_bbe(_sc: Scanner) -> Command:
        return BbeCommand()

    @staticmethod
    def _scan_sev(sc: Scanner) -> Command:
        param = sc.scan_number()
        sc.expect("|")
        number = sc.scan_number()
        sc.expect("|")
        return SevCommand(param, number)

    @staticmethod
    def _scan_bev(sc: Scanner) -> Command:
        param = sc.scan_until({"|"})
        return BevCommand(param)

    @staticmethod
    def _scan_wait(sc: Scanner) -> Command:
        time = sc.scan_number()
        return WaitCommand(time)

    @staticmethod
    def _scan_marriage(sc: Scanner) -> Command:
        return MarriageCommand(sc.scan_until({"|"}))

    @staticmethod
    def _scan_visual_effect(sc: Scanner) -> Command:
        return VisualEffectCommand(sc.scan_until({"|"}))

    @staticmethod
    def _scan_visual_effect_2(sc: Scanner) -> Command:
        return VisualEffect2Command(sc.scan_until({"|"}))

    @staticmethod
    def _scan_fade_white(sc: Scanner) -> Command:
        return FadeWhiteCommand(sc.scan_number())

    @staticmethod
    def _scan_fade_out(sc: Scanner) -> Command:
        return FadeOutCommand(sc.scan_number())

    @staticmethod
    def _scan_fade_in(sc: Scanner) -> Command:
        return FadeInCommand(sc.scan_number())

    @staticmethod
    def _scan_set_talk_window_panicked(_sc: Scanner) -> Command:
        return SetTalkWindowPanickedCommand()

    @staticmethod
    def _scan_synchronize(_sc: Scanner) -> Command:
        return SynchronizeCommand()

    @staticmethod
    def _scan_delete_speaker(_sc: Scanner) -> Command:
        return DeleteSpeakerCommand()

    @staticmethod
    def _scan_set_talk_window_scroll_in(_sc: Scanner) -> Command:
        return SetTalkWindowScrollInCommand()

    @staticmethod
    def _scan_print_avatar(_sc: Scanner) -> Command:
        return PrintAvatarCommand()

    @staticmethod
    def _scan_print_avatar_2(_sc: Scanner) -> Command:
        return PrintAvatar2Command()

    @staticmethod
    def _scan_print_online_player(sc: Scanner) -> Command:
        return PrintOnlinePlayerCommand(sc.scan_number())

    @staticmethod
    def _scan_fid_alias(sc: Scanner) -> Command:
        return FidAliasCommand(sc.scan_until({"|"}))

    @staticmethod
    def _scan_alias(sc: Scanner) -> Command:
        return AliasCommand(sc.scan_until({"|"}))

    @staticmethod
    def _scan_set_speaker(sc: Scanner) -> Command:
        return SetSpeakerCommand(sc.scan_until({"|"}))

    @staticmethod
    def _scan_load_assets(sc: Scanner) -> Command:
        param = sc.scan_until({"|"})
        sc.expect("|")
        if sc.peek() == "h":
            position = sc.next()
        else:
            position = sc.scan_number()
        return LoadAssetsCommand(param, position)

    @staticmethod
    def _scan_play_voice(sc: Scanner) -> Command:
        return PlayVoiceCommand(sc.scan_until({"|"}))

    @staticmethod
    def _scan_play_voice_japanese(sc: Scanner) -> Command:
        return PlayVoiceJapaneseCommand(sc.scan_until({"|"}))

    @staticmethod
    def _scan_play_voice_english(sc: Scanner) -> Command:
        return PlayVoiceEnglishCommand(sc.scan_until({"|"}))

    @staticmethod
    def _scan_play_sound_effect(sc: Scanner) -> Command:
        return PlaySoundEffectCommand(sc.scan_until({"|"}))

    @staticmethod
    def _scan_play_sound_effect_2(sc: Scanner) -> Command:
        return PlaySoundEffect2Command(sc.scan_until({"|"}))

    @staticmethod
    def _scan_play_music(sc: Scanner) -> Command:
        music = sc.scan_until({"|"})
        sc.expect("|")
        delay = sc.scan_number()
        sc.expect("|")
        return PlayMusicCommand(music, delay)

    @staticmethod
    def _scan_stop_music(sc: Scanner) -> Command:
        return StopMusicCommand(sc.scan_number())

    @staticmethod
    def _scan_set_volume(sc: Scanner) -> Command:
        volume = sc.scan_number()
        sc.expect("|")
        delay = sc.scan_number()
        sc.expect("|")
        return SetVolumeCommand(volume, delay)

    @staticmethod
    def _scan_dramatic_line(sc: Scanner) -> Command:
        return DramaticLineCommand(sc.scan_number())

    @staticmethod
    def _scan_dramatic_music(sc: Scanner) -> Command:
        music = sc.scan_until({"|"})
        sc.expect("|")
        volume = sc.scan_number()
        sc.expect("|")
        return DramaticMusicCommand(music, volume)

    @staticmethod
    def _scan_play_ramp(sc: Scanner) -> Command:
        music = sc.scan_until({"|"})
        sc.expect("|")
        time = sc.scan_number()
        sc.expect("|")
        return PlayRampCommand(music, time)

    @staticmethod
    def _scan_stop_ramp(sc: Scanner) -> Command:
        music = sc.scan_until({"|"})
        sc.expect("|")
        delay = sc.scan_number()
        sc.expect("|")
        return StopRampCommand(music, delay)

    @staticmethod
    def _scan_set_ramp_volume(sc: Scanner) -> Command:
        music = sc.scan_until({"|"})
        sc.expect("|")
        volume = sc.scan_number()
        sc.expect("|")
        delay = sc.scan_number()
        sc.expect("|")
        return SetRampVolumeCommand(music, volume, delay)

    def _scan_print(self, sc: Scanner):
        res = ""
        while sc.peek() != "$" and sc.peek() != "\0" and not self._next_is_newline(sc):
            res += sc.next()
        return PrintCommand(res)
