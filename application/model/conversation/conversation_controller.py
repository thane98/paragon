from typing import Optional, List, Dict

from model.message_archive import MessageArchive
from services.service_locator import locator
from ui.widgets.fe14_conversation_widget import FE14ConversationWidget


class Speaker:
    def __init__(self, fid: str, display_name: str, position: int):
        self.fid: str = fid
        self.display_name: str = display_name
        self.position: int = position
        self.emotions: List[str] = []

    def __repr__(self):
        return "<Speaker %s %s %d>" % (self.fid, self.display_name, self.position)


class ConversationController:
    def __init__(self, view):
        self.view: FE14ConversationWidget = view
        self._speakers: Dict[str, Speaker] = {}
        self._active_speaker: Optional[str] = None
        self._next_message = ""
        self._name_archive: MessageArchive = \
            locator.get_scoped("OpenFilesService").open_message_archive("m/GameData.bin.lz")

    def reset(self):
        self.view.clear()
        self._speakers.clear()
        self._active_speaker = None
        self._next_message = ""

    def create_speaker(self, fid_suffix):
        fid = "FID_" + fid_suffix
        portrait_entry = locator.get_scoped("PortraitService").get_portrait_entry_for_fid(fid, "st")
        display_name = portrait_entry["Name"].value
        speaker = Speaker(fid, display_name, 3)
        self.view.set_portraits(fid, speaker.position)
        self._speakers[fid_suffix] = speaker
        self._active_speaker = fid_suffix

    def set_active_speaker(self, new_speaker: str):
        if new_speaker not in self._speakers:
            raise ValueError("Speaker does not exist.")
        self._active_speaker = new_speaker

    def delete_active_speaker(self):
        del self._speakers[self._active_speaker]

    def reposition_active_speaker(self, new_position: int):
        self._speakers[self._active_speaker].position = new_position

    def set_emotions(self, new_emotions: List[str]):
        self._speakers[self._active_speaker].emotions = new_emotions

    def push_message(self, message: str):
        self._next_message += message

    def dump(self):
        self.view.clear()
        for speaker in self._speakers.values():
            self.view.set_portraits(speaker.fid, speaker.position)
            self.view.set_emotions(speaker.emotions, speaker.position)
        active_speaker = self._speakers[self._active_speaker]
        self.view.message(self._next_message, active_speaker.display_name, active_speaker.position)
        self._next_message = ""
