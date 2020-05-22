from abc import ABC, abstractmethod
from typing import List

from model.conversation.conversation_controller import ConversationController


class Command(ABC):
    @abstractmethod
    def run(self, controller: ConversationController):
        pass

    @abstractmethod
    def to_game_script(self) -> str:
        pass

    def is_pause(self) -> bool:
        return False


class PlayerMentionedCommand(Command):
    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$a"


class SetConversationTypeCommand(Command):
    def __init__(self, new_type: int):
        self.new_type = new_type

    def run(self, controller: ConversationController):
        pass  # TODO

    def to_game_script(self) -> str:
        return "$t" + str(self.new_type)


class LoadPortraitsCommand(Command):
    def __init__(self, portrait_name: str):
        self.portrait_name = portrait_name

    def run(self, controller: ConversationController):
        controller.create_speaker(self.portrait_name)

    def to_game_script(self) -> str:
        return "$Wm" + self.portrait_name


class RepositionSpeakerCommand(Command):
    def __init__(self, new_position: int):
        self.new_position = new_position

    def run(self, controller: ConversationController):
        controller.reposition_active_speaker(self.new_position)

    def to_game_script(self) -> str:
        return str(self.new_position)


class GetActiveSpeakerCommand(Command):
    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$w0"


class SetSpeakerCommand(Command):
    def __init__(self, new_speaker: str):
        self.new_speaker = new_speaker

    def run(self, controller: ConversationController):
        controller.set_active_speaker(self.new_speaker)

    def to_game_script(self) -> str:
        return "$Ws" + self.new_speaker


class SetEmotionCommand(Command):
    def __init__(self, new_emotions: List[str]):
        self.new_emotions = new_emotions

    def run(self, controller: ConversationController):
        controller.set_emotions(self.new_emotions)

    def to_game_script(self) -> str:
        return "$E%s," % ",".join(self.new_emotions)


class PlayVoiceCommand(Command):
    def __init__(self, voice_line: str):
        self.voice_line = voice_line

    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$Svp" + self.voice_line


class PlaySoundEffectCommand(Command):
    def __init__(self, effect_name: str):
        self.effect_name = effect_name

    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$Ssp" + self.effect_name


class PlayMusicCommand(Command):
    def __init__(self, music: str, delay: int):
        self.music = music
        self.delay = delay

    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$Sbp%s|%d|" % (self.music, self.delay)


class StopMusicCommand(Command):
    def __init__(self, delay: int):
        self.delay = delay

    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$Sbs" + str(self.delay)


class SetSpeakerAliasCommand(Command):
    def __init__(self, new_mpid: str):
        self.new_mpid = new_mpid

    def run(self, controller: ConversationController):
        controller.set_active_speaker_alias(self.new_mpid)

    def to_game_script(self) -> str:
        return "$VN" + self.new_mpid


class SetMessageColorCommand(Command):
    def __init__(self, new_color: str):
        self.new_color = new_color

    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$c" + self.new_color


class GenderDependentMessageCommand(Command):
    def __init__(self, message_1, message_2):
        self.message_1 = message_1
        self.message_2 = message_2

    def run(self, controller: ConversationController):
        pass  # TODO

    def to_game_script(self) -> str:
        return "$G%s,%s" % (self.message_1, self.message_2)


class PrintCommand(Command):
    def __init__(self, message: str):
        self.message = message

    def run(self, controller: ConversationController):
        controller.push_message(self.message)

    def to_game_script(self) -> str:
        return self.message


class PrintAvatarNameCommand(Command):
    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$Nu"


class PlayMessageCommand(Command):
    def run(self, controller: ConversationController):
        controller.dump()

    def to_game_script(self) -> str:
        return ""


class PauseCommand(Command):
    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$k"

    def is_pause(self) -> bool:
        return True


class PauseNewlineCommand(Command):
    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return r"$k\n"

    def is_pause(self) -> bool:
        return True


class ClearMessageCommand(Command):
    def run(self, controller: ConversationController):
        controller.set_window_type(0)

    def to_game_script(self) -> str:
        return "$p"


class DeleteSpeakerCommand(Command):
    def run(self, controller: ConversationController):
        controller.delete_active_speaker()

    def to_game_script(self) -> str:
        return "$Wd"


class TerminateConversationImmediateCommand(Command):
    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$N0"


class TerminateConversationCommand(Command):
    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$N1"


class SynchronizeCommand(Command):
    def run(self, controller: ConversationController):
        pass  # TODO: Figure out what this actually does.

    def to_game_script(self) -> str:
        return "$Wa"


class SetTalkWindowPanickedCommand(Command):
    def run(self, controller: ConversationController):
        controller.set_window_type(1)

    def to_game_script(self) -> str:
        return "$Wv"


class SetTalkBoxScrollInCommand(Command):
    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$Wc"


class CutsceneActionCommand(Command):
    def __init__(self, action: str):
        self.action = action

    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$b" + self.action


class WaitCommand(Command):
    def __init__(self, milliseconds_to_wait: int):
        self.milliseconds_to_wait = milliseconds_to_wait

    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$w" + str(self.milliseconds_to_wait)


class AdjustSoundVolumeCommand(Command):
    def __init__(self, new_volume: int, delay: int):
        self.new_volume = new_volume
        self.delay = delay

    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$Sbv%d|%d" % (self.new_volume, self.delay)


# Cut the music and play a dramatic sound effect.
class DramaticLineCommand(Command):
    def __init__(self, volume: int):
        self.volume = volume

    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$Sre" + str(self.volume)


class ConditionalFIDCommand(Command):
    def __init__(self, param: str):
        self.param = param

    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$VF" + self.param


class PlayerMarriageSceneCommand(Command):
    def __init__(self, target_character: str):
        self.target_character = target_character

    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$l" + self.target_character
