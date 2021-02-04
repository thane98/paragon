from typing import List

from paragon.core.dialogue.commands import *
from paragon.core.dialogue.scanner import Scanner


def _wrapped_scan(sc: Scanner, fn):
    sc.skip_whitespace()
    res = fn()
    sc.skip_whitespace()
    return res


def _scan_string(sc: Scanner):
    return _wrapped_scan(sc, lambda: sc.scan_until({",", ")", " ", "\t", "\r", "\n"}))


class PrettyScriptParser:
    def __init__(self):
        self.print_commands = {"a", "G", "Nu", "Np", "Nl", "c"}
        self.command_scanners = {
            "a": self._scan_param,
            "HasPermanents": self._scan_has_permanents,
            "Overworld": self._scan_overworld,
            "c": self._scan_color,
            "SetConversationType": self._scan_set_conversation_type,
            "Emotions": self._scan_set_emotions,
            "G": self._scan_print_gender_dependent,
            "Pause": self._scan_pause,
            "Clear": self._scan_clear,
            "Wf": self._scan_wf,
            "C": self._scan_c,
            "Bbs": self._scan_bbs,
            "Bbe": self._scan_bbe,
            "Sev": self._scan_sev,
            "Bev": self._scan_bev,
            "Wait": self._scan_wait,
            "Marriage": self._scan_marriage,
            "VisualEffect": self._scan_visual_effect,
            "VisualEffect2": self._scan_visual_effect_2,
            "FadeWhite": self._scan_fade_white,
            "FadeIn": self._scan_fade_in,
            "FadeOut": self._scan_fade_out,
            "Panicked": self._scan_set_talk_window_panicked,
            "Synchronize": self._scan_synchronize,
            "DeleteSpeaker": self._scan_delete_speaker,
            "ScrollIn": self._scan_set_talk_window_scroll_in,
            "Nu": self._scan_print_avatar,
            "Np": self._scan_print_avatar_2,
            "Nl": self._scan_print_online_player,
            "FidAlias": self._scan_fid_alias,
            "Alias": self._scan_alias,
            "SetSpeaker": self._scan_set_speaker,
            "LoadAssets": self._scan_load_assets,
            "PlayVoice": self._scan_play_voice,
            "PlayVoiceJapanese": self._scan_play_voice_japanese,
            "PlayVoiceEnglish": self._scan_play_voice_english,
            "PlaySoundEffect": self._scan_play_sound_effect,
            "PlaySoundEffect2": self._scan_play_sound_effect_2,
            "PlayMusic": self._scan_play_music,
            "StopMusic": self._scan_stop_music,
            "SetVolume": self._scan_set_volume,
            "DramaticLine": self._scan_dramatic_line,
            "DramaticMusic": self._scan_dramatic_music,
            "PlayRamp": self._scan_play_ramp,
            "StopRamp": self._scan_stop_ramp,
            "SetRampVolume": self._scan_set_ramp_volume,
        }

    def scan(self, input: str):
        if not input:
            return []
        sc = Scanner(input)
        commands = []
        while not sc.at_end():
            sc.skip_while({"\r", "\n"})
            next_print = self._scan_print(sc)
            if next_print.text and not next_print.text.isspace():
                commands.append(next_print)
                commands.extend(self._scan_print_line(sc))
            else:
                if sc.at_end():
                    pass  # Hit end after clearing whitespace. Done.
                elif sc.peek() == "\\" and sc.peek(1) == "n":
                    commands.append(self._scan_newline(sc))
                elif sc.peek() == "$":
                    two = sc.peek(1) + sc.peek(2)
                    one = sc.peek(1)
                    if two in self.print_commands or one in self.print_commands:
                        commands.extend(self._scan_print_line(sc))
                    else:
                        commands.append(self._scan_command(sc))
                else:
                    commands.extend(self._scan_print_line(sc))
        return commands

    def _scan_command(self, sc: Scanner) -> Command:
        sc.expect("$")
        command = sc.scan_alnum()
        if command in self.command_scanners:
            return self.command_scanners[command](sc)
        else:
            sc.error(f"Unrecognized command {command}.")

    def _scan_print_line(self, sc: Scanner) -> List[Command]:
        commands = []
        while sc.peek() not in {"\n", "\r", "\0"}:
            if sc.peek() == "$":
                sc.expect("$")
                two = sc.peek() + sc.peek(1)
                one = sc.peek()
                if two in self.print_commands:
                    sc.advance(2)
                    commands.append(self.command_scanners[two](sc))
                elif one in self.print_commands:
                    sc.advance(1)
                    commands.append(self.command_scanners[one](sc))
                else:
                    sc.error(f"Unrecognized command {sc.scan_alnum()}.")
            elif sc.peek() == "\\" and sc.peek(1) == "n":
                commands.append(self._scan_newline(sc))
            elif sc.peek() == "\\":
                commands.append(
                    PrintCommand(sc.next())
                )  # Workaround for Awakening weirdness.
            else:
                commands.append(self._scan_print(sc))
        return commands

    @staticmethod
    def _scan_newline(sc: Scanner) -> Command:
        sc.expect("\\")
        sc.expect("n")
        return NewlineCommand()

    @staticmethod
    def _scan_param(sc: Scanner) -> Command:
        sc.expect("(")
        number = _wrapped_scan(sc, lambda: sc.scan_number())
        sc.expect(")")
        return ParamCommand(number)

    @staticmethod
    def _scan_has_permanents(_sc: Scanner) -> Command:
        return HasPermanentsCommand()

    @staticmethod
    def _scan_overworld(_sc: Scanner) -> Command:
        return OverworldCommand()

    @staticmethod
    def _scan_color(sc: Scanner) -> Command:
        sc.expect("(")
        r = _wrapped_scan(sc, lambda: sc.scan_number())
        sc.expect(",")
        g = _wrapped_scan(sc, lambda: sc.scan_number())
        sc.expect(",")
        b = _wrapped_scan(sc, lambda: sc.scan_number())
        sc.expect(",")
        a = _wrapped_scan(sc, lambda: sc.scan_number())
        sc.expect(")")
        return ColorCommand(r, g, b, a)

    @staticmethod
    def _scan_set_conversation_type(sc: Scanner) -> Command:
        sc.expect("(")
        number = _wrapped_scan(sc, lambda: sc.scan_number())
        sc.expect(")")
        return SetConversationTypeCommand(number)

    @staticmethod
    def _scan_set_emotions(sc: Scanner) -> Command:
        emotions = []
        sc.expect("(")
        while sc.peek() != ")":
            emotion = _scan_string(sc)
            if sc.peek() != ")":
                sc.expect(",")
            emotions.append(emotion)
        sc.expect(")")
        return SetEmotionsCommand(emotions)

    @staticmethod
    def _scan_print_gender_dependent(sc: Scanner) -> Command:
        sc.expect("(")
        m = sc.scan_until({","})
        sc.expect(",")
        f = sc.scan_until({")"})
        sc.expect(")")
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
        sc.expect("(")
        a = _wrapped_scan(sc, lambda: sc.scan_number())
        sc.expect(",")
        b = _wrapped_scan(sc, lambda: sc.scan_number())
        sc.expect(",")
        c = _wrapped_scan(sc, lambda: sc.scan_number())
        sc.expect(")")
        return BbsCommand(a, b, c)

    @staticmethod
    def _scan_bbe(_sc: Scanner) -> Command:
        return BbeCommand()

    @staticmethod
    def _scan_sev(sc: Scanner) -> Command:
        sc.expect("(")
        param = _wrapped_scan(sc, lambda: sc.scan_number())
        sc.expect(",")
        number = _wrapped_scan(sc, lambda: sc.scan_number())
        sc.expect(")")
        return SevCommand(param, number)

    @staticmethod
    def _scan_bev(sc: Scanner) -> Command:
        sc.expect("{")
        param = sc.scan_until({"}"})
        sc.expect("}")
        return BevCommand(param)

    @staticmethod
    def _scan_wait(sc: Scanner) -> Command:
        sc.expect("(")
        number = _wrapped_scan(sc, lambda: sc.scan_number())
        sc.expect(")")
        return WaitCommand(number)

    @staticmethod
    def _scan_marriage(sc: Scanner) -> Command:
        sc.expect("(")
        param = _scan_string(sc)
        sc.expect(")")
        return MarriageCommand(param)

    @staticmethod
    def _scan_visual_effect(sc: Scanner) -> Command:
        sc.expect("(")
        param = _scan_string(sc)
        sc.expect(")")
        return VisualEffectCommand(param)

    @staticmethod
    def _scan_visual_effect_2(sc: Scanner) -> Command:
        sc.expect("(")
        param = _scan_string(sc)
        sc.expect(")")
        return VisualEffect2Command(param)

    @staticmethod
    def _scan_fade_white(sc: Scanner) -> Command:
        sc.expect("(")
        number = _wrapped_scan(sc, lambda: sc.scan_number())
        sc.expect(")")
        return FadeWhiteCommand(number)

    @staticmethod
    def _scan_fade_out(sc: Scanner) -> Command:
        sc.expect("(")
        number = _wrapped_scan(sc, lambda: sc.scan_number())
        sc.expect(")")
        return FadeOutCommand(number)

    @staticmethod
    def _scan_fade_in(sc: Scanner) -> Command:
        sc.expect("(")
        number = _wrapped_scan(sc, lambda: sc.scan_number())
        sc.expect(")")
        return FadeInCommand(number)

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
        sc.expect("(")
        number = _wrapped_scan(sc, lambda: sc.scan_number())
        sc.expect(")")
        return PrintOnlinePlayerCommand(number)

    @staticmethod
    def _scan_fid_alias(sc: Scanner) -> Command:
        sc.expect("(")
        param = _scan_string(sc)
        sc.expect(")")
        return FidAliasCommand(param)

    @staticmethod
    def _scan_alias(sc: Scanner) -> Command:
        sc.expect("(")
        param = _scan_string(sc)
        sc.expect(")")
        return AliasCommand(param)

    @staticmethod
    def _scan_set_speaker(sc: Scanner) -> Command:
        sc.expect("(")
        param = _scan_string(sc)
        sc.expect(")")
        return SetSpeakerCommand(param)

    @staticmethod
    def _scan_load_assets(sc: Scanner) -> Command:
        sc.expect("(")
        param = _scan_string(sc)
        sc.expect(",")
        sc.skip_whitespace()
        if sc.peek() == "h":
            position = sc.next()
            sc.skip_whitespace()
        else:
            position = sc.scan_number()
            sc.skip_whitespace()
        sc.expect(")")
        return LoadAssetsCommand(param, position)

    @staticmethod
    def _scan_play_voice(sc: Scanner) -> Command:
        sc.expect("(")
        param = _scan_string(sc)
        sc.expect(")")
        return PlayVoiceCommand(param)

    @staticmethod
    def _scan_play_voice_japanese(sc: Scanner) -> Command:
        sc.expect("(")
        param = _scan_string(sc)
        sc.expect(")")
        return PlayVoiceJapaneseCommand(param)

    @staticmethod
    def _scan_play_voice_english(sc: Scanner) -> Command:
        sc.expect("(")
        param = _scan_string(sc)
        sc.expect(")")
        return PlayVoiceEnglishCommand(param)

    @staticmethod
    def _scan_play_sound_effect(sc: Scanner) -> Command:
        sc.expect("(")
        param = _scan_string(sc)
        sc.expect(")")
        return PlaySoundEffectCommand(param)

    @staticmethod
    def _scan_play_sound_effect_2(sc: Scanner) -> Command:
        sc.expect("(")
        param = _scan_string(sc)
        sc.expect(")")
        return PlaySoundEffect2Command(param)

    @staticmethod
    def _scan_play_music(sc: Scanner) -> Command:
        sc.expect("(")
        music = _scan_string(sc)
        sc.expect(",")
        delay = _wrapped_scan(sc, lambda: sc.scan_number())
        sc.expect(")")
        return PlayMusicCommand(music, delay)

    @staticmethod
    def _scan_stop_music(sc: Scanner) -> Command:
        sc.expect("(")
        number = _wrapped_scan(sc, lambda: sc.scan_number())
        sc.expect(")")
        return StopMusicCommand(number)

    @staticmethod
    def _scan_set_volume(sc: Scanner) -> Command:
        sc.expect("(")
        volume = _wrapped_scan(sc, lambda: sc.scan_number())
        sc.expect(",")
        delay = _wrapped_scan(sc, lambda: sc.scan_number())
        sc.expect(")")
        return SetVolumeCommand(volume, delay)

    @staticmethod
    def _scan_dramatic_line(sc: Scanner) -> Command:
        sc.expect("(")
        number = _wrapped_scan(sc, lambda: sc.scan_number())
        sc.expect(")")
        return DramaticLineCommand(number)

    @staticmethod
    def _scan_dramatic_music(sc: Scanner) -> Command:
        sc.expect("(")
        music = _scan_string(sc)
        sc.expect(",")
        volume = _wrapped_scan(sc, lambda: sc.scan_number())
        sc.expect(")")
        return DramaticMusicCommand(music, volume)

    @staticmethod
    def _scan_play_ramp(sc: Scanner) -> Command:
        sc.expect("(")
        music = _scan_string(sc)
        sc.expect(",")
        time = _wrapped_scan(sc, lambda: sc.scan_number())
        sc.expect(")")
        return PlayRampCommand(music, time)

    @staticmethod
    def _scan_stop_ramp(sc: Scanner) -> Command:
        sc.expect("(")
        music = _scan_string(sc)
        sc.expect(",")
        delay = _wrapped_scan(sc, lambda: sc.scan_number())
        sc.expect(")")
        return StopRampCommand(music, delay)

    @staticmethod
    def _scan_set_ramp_volume(sc: Scanner) -> Command:
        sc.expect("(")
        music = _scan_string(sc)
        sc.expect(",")
        volume = _wrapped_scan(sc, lambda: sc.scan_number())
        sc.expect(",")
        delay = _wrapped_scan(sc, lambda: sc.scan_number())
        sc.expect(")")
        return SetRampVolumeCommand(music, volume, delay)

    @staticmethod
    def _scan_print(sc: Scanner) -> PrintCommand:
        text = sc.scan_until({"\\", "$", "\r", "\n", "\0"})
        return PrintCommand(text)
