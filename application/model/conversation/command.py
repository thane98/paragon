from abc import ABC, abstractmethod
from typing import List

from model.conversation.conversation_controller import ConversationController
from services.service_locator import locator


class Command(ABC):
    @abstractmethod
    def run(self, controller: ConversationController):
        pass

    @abstractmethod
    def to_game_script(self) -> str:
        pass

    @abstractmethod
    def to_paragon_script(self) -> str:
        pass

    def is_pause(self) -> bool:
        return False


class PlayerMentionedCommand(Command):
    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$a"

    def to_paragon_script(self) -> str:
        return "HasPermanents"


class SetConversationTypeCommand(Command):
    def __init__(self, new_type: int):
        self.new_type = new_type

    def run(self, controller: ConversationController):
        pass  # TODO

    def to_game_script(self) -> str:
        return "$t" + str(self.new_type)

    def to_paragon_script(self) -> str:
        return "ConversationType " + str(self.new_type)


class LoadPortraitsCommand(Command):
    def __init__(self, portrait_name: str):
        self.portrait_name = portrait_name

    def run(self, controller: ConversationController):
        controller.create_speaker(self.portrait_name)

    def to_game_script(self) -> str:
        return "$Wm%s|" % self.portrait_name

    def to_paragon_script(self) -> str:
        conversation_service = locator.get_scoped("ConversationService")
        return "NewSpeaker " + conversation_service.translate_speaker_name_to_english(self.portrait_name)


class RepositionSpeakerCommand(Command):
    def __init__(self, new_position: int):
        self.new_position = new_position

    def run(self, controller: ConversationController):
        controller.reposition_active_speaker(self.new_position)

    def to_game_script(self) -> str:
        return str(self.new_position)

    def to_paragon_script(self) -> str:
        return "Reposition " + str(self.new_position)


class SetSpeakerCommand(Command):
    def __init__(self, new_speaker: str):
        self.new_speaker = new_speaker

    def run(self, controller: ConversationController):
        controller.set_active_speaker(self.new_speaker)

    def to_game_script(self) -> str:
        return "$Ws%s|" % self.new_speaker

    def to_paragon_script(self) -> str:
        conversation_service = locator.get_scoped("ConversationService")
        return "SetSpeaker " + conversation_service.translate_speaker_name_to_english(self.new_speaker)


class SetEmotionCommand(Command):
    def __init__(self, new_emotions: List[str]):
        self.new_emotions = new_emotions

    def run(self, controller: ConversationController):
        controller.set_emotions(self.new_emotions)

    def to_game_script(self) -> str:
        return "$Wa$E%s|" % ",".join(self.new_emotions)

    def to_paragon_script(self) -> str:
        conversation_service = locator.get_scoped("ConversationService")
        emotions = conversation_service.translate_emotions_to_english(self.new_emotions)
        return "Emotions(%s)" % ",".join(emotions)


class PlayVoiceCommand(Command):
    def __init__(self, voice_line: str):
        self.voice_line = voice_line

    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$Svp%s|" % self.voice_line

    def to_paragon_script(self) -> str:
        return "PlayVoice %s" % self.voice_line


class PlaySoundEffectCommand(Command):
    def __init__(self, effect_name: str):
        self.effect_name = effect_name

    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$Ssp%s|" % self.effect_name

    def to_paragon_script(self) -> str:
        return "PlaySoundEffect %s" % self.effect_name


class PlayMusicCommand(Command):
    def __init__(self, music: str, delay: int):
        self.music = music
        self.delay = delay

    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$Sbp%s|%d|" % (self.music, self.delay)

    def to_paragon_script(self) -> str:
        return "PlayMusic(%s, %d)" % (self.music, self.delay)


class StopMusicCommand(Command):
    def __init__(self, delay: int):
        self.delay = delay

    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$Sbs%s|" % str(self.delay)

    def to_paragon_script(self) -> str:
        return "StopMusic %d" % self.delay


class SetSpeakerAliasCommand(Command):
    def __init__(self, new_mpid: str):
        self.new_mpid = new_mpid

    def run(self, controller: ConversationController):
        controller.set_active_speaker_alias(self.new_mpid)

    def to_game_script(self) -> str:
        return "$VN%s|" % self.new_mpid

    def to_paragon_script(self) -> str:
        return "Alias %s" % self.new_mpid


class GenderDependentMessageCommand(Command):
    def __init__(self, message_1, message_2):
        self.message_1 = message_1
        self.message_2 = message_2

    def run(self, controller: ConversationController):
        conversation_service = locator.get_scoped("ConversationService")
        if conversation_service.avatar_is_female():
            controller.push_message(self.message_2)
        else:
            controller.push_message(self.message_1)

    def to_game_script(self) -> str:
        return "$G%s,%s|" % (self.message_1, self.message_2)

    def to_paragon_script(self) -> str:
        return "G(%s, %s)" % (self.message_1, self.message_2)


class PrintCommand(Command):
    def __init__(self, message: str):
        self.message = message

    def run(self, controller: ConversationController):
        controller.push_message(self.message)

    def to_game_script(self) -> str:
        return self.message

    def to_paragon_script(self) -> str:
        return self.message.replace(r"\n", "\n")


class PrintAvatarNameCommand(Command):
    def run(self, controller: ConversationController):
        conversation_service = locator.get_scoped("ConversationService")
        controller.push_message(conversation_service.get_avatar_name())

    def to_game_script(self) -> str:
        return "$Nu"

    def to_paragon_script(self) -> str:
        return "Nu"


class PlayMessageCommand(Command):
    def run(self, controller: ConversationController):
        controller.dump()

    def to_game_script(self) -> str:
        return ""

    def to_paragon_script(self) -> str:
        return ""


class PauseCommand(Command):
    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$k"

    def to_paragon_script(self) -> str:
        return "Await"

    def is_pause(self) -> bool:
        return True


class PauseNewlineCommand(Command):
    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$k\n"

    def to_paragon_script(self) -> str:
        return "AwaitAndClear"

    def is_pause(self) -> bool:
        return True


class ClearMessageCommand(Command):
    def run(self, controller: ConversationController):
        controller.set_window_type(0)

    def to_game_script(self) -> str:
        return "$p"

    def to_paragon_script(self) -> str:
        return "Clear"


class DeleteSpeakerCommand(Command):
    def run(self, controller: ConversationController):
        controller.delete_active_speaker()

    def to_game_script(self) -> str:
        return "$Wd"

    def to_paragon_script(self) -> str:
        return "DeleteSpeaker"


class SynchronizeCommand(Command):
    def run(self, controller: ConversationController):
        pass  # TODO: Figure out what this actually does.

    def to_game_script(self) -> str:
        return "$Wa"

    def to_paragon_script(self) -> str:
        return ""


class SetTalkWindowPanickedCommand(Command):
    def run(self, controller: ConversationController):
        controller.set_window_type(1)

    def to_game_script(self) -> str:
        return "$Wv"

    def to_paragon_script(self) -> str:
        return "Panicked"


class SetTalkBoxScrollInCommand(Command):
    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$Wc"

    def to_paragon_script(self) -> str:
        return "Scrolling"


class CutsceneActionCommand(Command):
    def __init__(self, action: str):
        self.action = action

    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$b%s;|" % self.action

    def to_paragon_script(self) -> str:
        return "CutsceneAction " + self.action


class WaitCommand(Command):
    def __init__(self, milliseconds_to_wait: int):
        self.milliseconds_to_wait = milliseconds_to_wait

    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$w%d|" % self.milliseconds_to_wait

    def to_paragon_script(self) -> str:
        return "Wait " + str(self.milliseconds_to_wait)


class AdjustSoundVolumeCommand(Command):
    def __init__(self, new_volume: int, delay: int):
        self.new_volume = new_volume
        self.delay = delay

    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$Sbv%d|%d|" % (self.new_volume, self.delay)

    def to_paragon_script(self) -> str:
        return "Volume(%d, %d)" % (self.new_volume, self.delay)


# Cut the music and play a dramatic sound effect.
class DramaticLineCommand(Command):
    def __init__(self, volume: int):
        self.volume = volume

    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$Sre%d|" % self.volume

    def to_paragon_script(self) -> str:
        return "Dramatic %d" % self.volume


class ConditionalFIDCommand(Command):
    def __init__(self, param: str):
        self.param = param

    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$VF%s|" % self.param

    def to_paragon_script(self) -> str:
        return "OverridePortrait %s" % self.param


class PlayerMarriageSceneCommand(Command):
    def __init__(self, target_character: str):
        self.target_character = target_character

    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$l" + self.target_character

    def to_paragon_script(self) -> str:
        return "ShowMarriageScene"


class PlayMusicWithVolumeRampCommand(Command):
    def __init__(self, music: str, ramp_time_milliseconds: int):
        self.music = music
        self.ramp_time_milliseconds = ramp_time_milliseconds

    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$Slp%s|%d|" % (self.music, self.ramp_time_milliseconds)

    def to_paragon_script(self) -> str:
        return "Ramp(%s, %d)" % (self.music, self.ramp_time_milliseconds)


class CancelMusicRampCommand(Command):
    def __init__(self, music: str, delay: int):
        self.music = music
        self.delay = delay

    def run(self, controller: ConversationController):
        pass

    def to_game_script(self) -> str:
        return "$Sls%s|%d|" % (self.music, self.delay)

    def to_paragon_script(self) -> str:
        return "StopRamp(%s, %d)" % (self.music, self.delay)
