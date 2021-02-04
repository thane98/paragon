from paragon.model.dialogue_interpreter_state import DialogueInterpreterState


class Command:
    def to_game(self) -> str:
        raise NotImplementedError

    def to_pretty(self) -> str:
        raise NotImplementedError

    def is_print(self) -> bool:
        return False

    def interpret(self, state: DialogueInterpreterState):
        pass


class NewlineCommand(Command):
    def to_game(self) -> str:
        return r"\n"

    def to_pretty(self) -> str:
        return r"\n"

    def interpret(self, state: DialogueInterpreterState):
        state.newline()


class ParamCommand(Command):
    def __init__(self, param: int):
        self.param = param

    def to_game(self) -> str:
        return "$a" + str(self.param)

    def to_pretty(self) -> str:
        return f"$a({self.param})"

    def is_print(self) -> bool:
        return True

    def interpret(self, state: DialogueInterpreterState):
        state.append(self.to_game())


class HasPermanentsCommand(Command):
    def to_game(self) -> str:
        return "$a"

    def to_pretty(self) -> str:
        return "$HasPermanents"


class OverworldCommand(Command):
    def to_game(self) -> str:
        return "$Z"

    def to_pretty(self) -> str:
        return "$Overworld"


class ColorCommand(Command):
    def __init__(self, r, g, b, a):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def to_game(self) -> str:
        return f"$c{self.r},{self.g},{self.b},{self.a}|"

    def to_pretty(self) -> str:
        return f"$c({self.r},{self.g},{self.b},{self.a})"

    def is_print(self) -> bool:
        return True


class SetConversationTypeCommand(Command):
    def __init__(self, t):
        self.t = t

    def to_game(self) -> str:
        return "$t" + str(self.t)

    def to_pretty(self) -> str:
        return f"$SetConversationType({self.t})"

    def interpret(self, state: DialogueInterpreterState):
        state.set_type(self.t)


class SetEmotionsCommand(Command):
    def __init__(self, emotions):
        self.emotions = emotions

    def to_game(self) -> str:
        return "$E" + ",".join(self.emotions) + "|"

    def to_pretty(self) -> str:
        return "$Emotions(%s)" % ",".join(self.emotions)

    def interpret(self, state: DialogueInterpreterState):
        state.set_emotions(self.emotions)


class PrintGenderDependentCommand(Command):
    def __init__(self, m, f):
        self.m = m
        self.f = f

    def to_game(self) -> str:
        return f"$G{self.m},{self.f}|"

    def to_pretty(self) -> str:
        return f"$G({self.m},{self.f})"

    def is_print(self) -> bool:
        return True

    def interpret(self, state: DialogueInterpreterState):
        state.append(self.m)  # TODO


class PauseCommand(Command):
    def to_game(self) -> str:
        return "$k"

    def to_pretty(self) -> str:
        return "$Pause"

    def interpret(self, state: DialogueInterpreterState):
        state.clear()


class ClearCommand(Command):
    def to_game(self) -> str:
        return "$p"

    def to_pretty(self) -> str:
        return "$Clear"

    def interpret(self, state: DialogueInterpreterState):
        state.clear()


class WfCommand(Command):
    def to_game(self) -> str:
        return "$Wf"

    def to_pretty(self) -> str:
        return "$Wf"


class CCommand(Command):
    def to_game(self) -> str:
        return "$C"

    def to_pretty(self) -> str:
        return "$C"


class BbsCommand(Command):
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def to_game(self) -> str:
        return f"$Bbs{self.a},{self.b},{self.c}|"

    def to_pretty(self) -> str:
        return f"$Bbs({self.a},{self.b},{self.c})"


class BbeCommand(Command):
    def to_game(self) -> str:
        return "$Bbe"

    def to_pretty(self) -> str:
        return "$Bbe"


class SevCommand(Command):
    def __init__(self, param, number):
        self.param = param
        self.number = number

    def to_game(self) -> str:
        return f"$Sev{self.param}|{self.number}"

    def to_pretty(self) -> str:
        return f"$Sev({self.param},{self.number})"


class BevCommand(Command):
    def __init__(self, param):
        self.param = param

    def to_game(self) -> str:
        return f"$b{self.param}|"

    def to_pretty(self) -> str:
        return f"$Bev{{{self.param}}}"


class WaitCommand(Command):
    def __init__(self, time):
        self.time = time

    def to_game(self):
        return f"$w{self.time}|"

    def to_pretty(self) -> str:
        return f"$Wait({self.time})"


class MarriageCommand(Command):
    def __init__(self, param):
        self.param = param

    def to_game(self):
        return f"$l{self.param}|"

    def to_pretty(self) -> str:
        return f"$Marriage({self.param})"


class VisualEffectCommand(Command):
    def __init__(self, param):
        self.param = param

    def to_game(self):
        return f"$Tc{self.param}|"

    def to_pretty(self) -> str:
        return f"$VisualEffect({self.param})"


class VisualEffect2Command(Command):
    def __init__(self, param):
        self.param = param

    def to_game(self):
        return f"$Td{self.param}|"

    def to_pretty(self) -> str:
        return f"$VisualEffect2({self.param})"


class FadeWhiteCommand(Command):
    def __init__(self, param):
        self.param = param

    def to_game(self):
        return f"$Fw{self.param}|"

    def to_pretty(self) -> str:
        return f"$FadeWhite({self.param})"


class FadeOutCommand(Command):
    def __init__(self, param):
        self.param = param

    def to_game(self):
        return f"$Fo{self.param}|"

    def to_pretty(self) -> str:
        return f"$FadeOut({self.param})"


class FadeInCommand(Command):
    def __init__(self, param):
        self.param = param

    def to_game(self):
        return f"$Fi{self.param}|"

    def to_pretty(self) -> str:
        return f"$FadeIn({self.param})"


class SetTalkWindowPanickedCommand(Command):
    def to_game(self) -> str:
        return "$Wv"

    def to_pretty(self) -> str:
        return "$Panicked"


class SynchronizeCommand(Command):
    def to_game(self) -> str:
        return "$Wa"

    def to_pretty(self) -> str:
        return "$Synchronize"


class DeleteSpeakerCommand(Command):
    def to_game(self) -> str:
        return "$Wd"

    def to_pretty(self) -> str:
        return "$DeleteSpeaker"

    def interpret(self, state: DialogueInterpreterState):
        state.delete_speaker()


class SetTalkWindowScrollInCommand(Command):
    def to_game(self) -> str:
        return "$Wc"

    def to_pretty(self) -> str:
        return "$ScrollIn"


class PrintAvatarCommand(Command):
    def to_game(self) -> str:
        return "$Nu"

    def to_pretty(self) -> str:
        return "$Nu"

    def is_print(self) -> bool:
        return True

    def interpret(self, state: DialogueInterpreterState):
        state.append("???")  # TODO


class PrintAvatar2Command(Command):
    def to_game(self) -> str:
        return "$Np"

    def to_pretty(self) -> str:
        return "$Np"

    def is_print(self) -> bool:
        return True

    def interpret(self, state: DialogueInterpreterState):
        state.append("???")  # TODO


class PrintOnlinePlayerCommand(Command):
    def __init__(self, param):
        self.param = param

    def to_game(self) -> str:
        return f"$Nl{self.param}"

    def to_pretty(self) -> str:
        return f"$Nl({self.param})"

    def is_print(self) -> bool:
        return True

    def interpret(self, state: DialogueInterpreterState):
        state.append("???")  # TODO


class FidAliasCommand(Command):
    def __init__(self, param):
        self.param = param

    def to_game(self) -> str:
        return f"$VF{self.param}|"

    def to_pretty(self) -> str:
        return f"$FidAlias({self.param})"

    def interpret(self, state: DialogueInterpreterState):
        state.set_fid_alias(self.param)


class AliasCommand(Command):
    def __init__(self, param):
        self.param = param

    def to_game(self) -> str:
        return f"$VN{self.param}|"

    def to_pretty(self) -> str:
        return f"$Alias({self.param})"

    def interpret(self, state: DialogueInterpreterState):
        state.set_alias(self.param)


class SetSpeakerCommand(Command):
    def __init__(self, speaker):
        self.speaker = speaker

    def to_game(self) -> str:
        return f"$Ws{self.speaker}|"

    def to_pretty(self) -> str:
        return f"$SetSpeaker({self.speaker})"

    def interpret(self, state: DialogueInterpreterState):
        state.set_active(self.speaker)


class LoadAssetsCommand(Command):
    def __init__(self, assets, position):
        self.assets = assets
        self.position = position

    def to_game(self) -> str:
        return f"$Wm{self.assets}|{self.position}"

    def to_pretty(self) -> str:
        return f"$LoadAssets({self.assets}, {self.position})"

    def interpret(self, state: DialogueInterpreterState):
        state.add_speaker(self.assets, self.position)


class PlayVoiceCommand(Command):
    def __init__(self, sound):
        self.sound = sound

    def to_game(self) -> str:
        return f"$Svp{self.sound}|"

    def to_pretty(self) -> str:
        return f"$PlayVoice({self.sound})"


class PlayVoiceJapaneseCommand(Command):
    def __init__(self, sound):
        self.sound = sound

    def to_game(self) -> str:
        return f"$Svj{self.sound}|"

    def to_pretty(self) -> str:
        return f"$PlayVoiceJapanese({self.sound})"


class PlayVoiceEnglishCommand(Command):
    def __init__(self, sound):
        self.sound = sound

    def to_game(self) -> str:
        return f"$Sve{self.sound}|"

    def to_pretty(self) -> str:
        return f"$PlayVoiceEnglish({self.sound})"


class PlaySoundEffectCommand(Command):
    def __init__(self, sound):
        self.sound = sound

    def to_game(self) -> str:
        return f"$Ssp{self.sound}|"

    def to_pretty(self) -> str:
        return f"$PlaySoundEffect({self.sound})"


class PlaySoundEffect2Command(Command):
    def __init__(self, sound):
        self.sound = sound

    def to_game(self) -> str:
        return f"$Ssw{self.sound}|"

    def to_pretty(self) -> str:
        return f"$PlaySoundEffect2({self.sound})"


class PlayMusicCommand(Command):
    def __init__(self, music, delay):
        self.music = music
        self.delay = delay

    def to_game(self) -> str:
        return f"$Sbp{self.music}|{self.delay}|"

    def to_pretty(self) -> str:
        return f"$PlayMusic({self.music},{self.delay})"


class StopMusicCommand(Command):
    def __init__(self, delay):
        self.delay = delay

    def to_game(self) -> str:
        return f"$Sbs{self.delay}|"

    def to_pretty(self) -> str:
        return f"$StopMusic({self.delay})"


class SetVolumeCommand(Command):
    def __init__(self, volume, delay):
        self.volume = volume
        self.delay = delay

    def to_game(self) -> str:
        return f"$Sbv{self.volume}|{self.delay}|"

    def to_pretty(self) -> str:
        return f"$SetVolume({self.volume},{self.delay})"


class DramaticLineCommand(Command):
    def __init__(self, volume):
        self.volume = volume

    def to_game(self) -> str:
        return f"$Sre{self.volume}|"

    def to_pretty(self) -> str:
        return f"$DramaticLine({self.volume})"


class DramaticMusicCommand(Command):
    def __init__(self, music, volume):
        self.music = music
        self.volume = volume

    def to_game(self) -> str:
        return f"$Srp{self.music}|{self.volume}|"

    def to_pretty(self) -> str:
        return f"$DramaticMusic({self.music},{self.volume})"


class PlayRampCommand(Command):
    def __init__(self, music, time):
        self.music = music
        self.time = time

    def to_game(self) -> str:
        return f"$Slp{self.music}|{self.time}|"

    def to_pretty(self) -> str:
        return f"$PlayRamp({self.music},{self.time})"


class StopRampCommand(Command):
    def __init__(self, music, delay):
        self.music = music
        self.delay = delay

    def to_game(self) -> str:
        return f"$Sls{self.music}|{self.delay}|"

    def to_pretty(self) -> str:
        return f"$StopRamp({self.music},{self.delay})"


class SetRampVolumeCommand(Command):
    def __init__(self, music, volume, delay):
        self.music = music
        self.volume = volume
        self.delay = delay

    def to_game(self) -> str:
        return f"$Slv{self.music}|{self.volume}|{self.delay}|"

    def to_pretty(self) -> str:
        return f"$SetRampVolume({self.music},{self.volume},{self.delay})"


class PrintCommand(Command):
    def __init__(self, text):
        self.text = text

    def to_game(self) -> str:
        return self.text

    def to_pretty(self) -> str:
        return self.text

    def is_print(self) -> bool:
        return True

    def interpret(self, state: DialogueInterpreterState):
        state.append(self.text)
