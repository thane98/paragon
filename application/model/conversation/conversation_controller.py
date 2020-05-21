from typing import Optional, List

from model.message_archive import MessageArchive
from services.service_locator import locator
from ui.widgets.fe14_conversation_widget import FE14ConversationWidget


class MessageStackEntry:
    def __init__(self):
        self.target_position: Optional[int] = None
        self.fid: Optional[str] = None
        self.emotion: Optional[str] = None
        self.message: str = ""
        self.display_name: str = ""

    def duplicate(self) -> "MessageStackEntry":
        copy = MessageStackEntry()
        copy.target_position = self.target_position
        copy.fid = self.fid
        copy.emotion = self.emotion
        copy.message = self.message
        copy.display_name = self.display_name
        return copy


class ConversationController:
    def __init__(self, view):
        self.view: FE14ConversationWidget = view
        self._message_stack: List[MessageStackEntry] = []
        self._name_archive: MessageArchive = \
            locator.get_scoped("OpenFilesService").open_message_archive("m/GameData.bin.lz")

    def push_message(self, message: str):
        self._message_stack[-1].message += message

    def push_portrait(self, fid_suffix: str):
        top = MessageStackEntry()
        top.fid = "FID_" + fid_suffix
        self._message_stack.append(top)

    def set_portrait_position(self, position: int):
        self._message_stack[-1].target_position = position

    def set_name(self, new_name: str):
        mpid = "MPID_" + new_name
        if self._name_archive.has_message(mpid):
            display_name = self._name_archive.get_message(mpid)
        else:
            display_name = "???"
        self._message_stack[-1].display_name = display_name

    def set_emotion(self, new_emotion: str):
        self._message_stack[-1].emotion = new_emotion

    def dump(self):
        if not self._message_stack:
            raise IndexError("Cannot dump message when the message stack is empty!")
        if not self._message_stack[-1].target_position or not self._message_stack[-1].fid:
            raise ValueError("Cannot dump message with a position or portrait!")  # TODO: This check can go away later.
        message = self._message_stack[-1]
        self.view.set_portraits(message.fid, message.target_position)
        self.view.set_emotion(message.emotion, message.target_position)
        self.view.message(message.message, message.display_name, message.target_position)
        self._message_stack.append(message.duplicate())
