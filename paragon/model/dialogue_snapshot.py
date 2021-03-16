import dataclasses
from copy import deepcopy
from typing import List, Optional
from paragon.model.speaker import Speaker


@dataclasses.dataclass
class DialogueSnapshot:
    conversation_type: int = 1
    speakers: List[Speaker] = dataclasses.field(default_factory=list)
    active: str = ""
    top: List[str] = dataclasses.field(init=False)
    bottom: List[str] = dataclasses.field(init=False)
    top_line: int = 0
    bottom_line: int = 0
    panicked: bool = False

    def __post_init__(self):
        self.top = ["", ""]
        self.bottom = ["", ""]
        self.speakers.append(Speaker.anonymous_speaker())

    def add_speaker(self, name, position):
        self.speakers = list(filter(lambda s: s.position != position, self.speakers))
        self.speakers.append(Speaker(name, position))

    def delete_speaker(self):
        speaker = next(filter(lambda s: s.name == self.active, self.speakers), None)
        if speaker and not speaker.is_anonymous():
            self.speakers.remove(speaker)
            self.active = ""

    def set_active(self, active):
        self.active = active

    def set_emotions(self, emotions):
        if speaker := self.active_speaker():
            speaker.emotions = emotions

    def set_fid_alias(self, fid_alias):
        if speaker := self.active_speaker():
            speaker.fid_alias = fid_alias

    def set_alias(self, alias):
        if speaker := self.active_speaker():
            speaker.alias = alias

    def append(self, message):
        if speaker := self.active_speaker():
            if self.is_end_of_message():
                self.clear_text()
            if speaker.is_top():
                self.top[self.top_line] += message
            else:
                self.bottom[self.bottom_line] += message

    def clear_text(self):
        if speaker := self.active_speaker():
            if speaker.is_top():
                self.top = ["", ""]
                self.top_line = 0
            else:
                self.bottom = ["", ""]
                self.bottom_line = 0

    def has_text(self):
        if speaker := self.active_speaker():
            if speaker.is_top():
                return self.top[0] or self.top[1]
            else:
                return self.bottom[0] or self.bottom[1]
        else:
            return False

    def is_end_of_message(self):
        if s := self.active_speaker():
            return self.top_line >= 2 if s.is_top() else self.bottom_line >= 2
        else:
            return False

    def next_line(self):
        if speaker := self.active_speaker():
            if speaker.is_top():
                self.top_line += 1
            else:
                self.bottom_line += 1

    def active_speaker(self):
        return next(filter(lambda s: s.name == self.active, self.speakers), None)

    def clone(self):
        return deepcopy(self)

    def top_speaker(self) -> Optional[Speaker]:
        if speaker := self.active_speaker():
            if speaker.is_top():
                return speaker
        return next(filter(lambda s: s.is_top(), reversed(self.speakers)), None)

    def bottom_speaker(self) -> Optional[Speaker]:
        if speaker := self.active_speaker():
            if speaker.is_bottom():
                return speaker
        return next(filter(lambda s: s.is_bottom(), reversed(self.speakers)), None)

    def top_text(self) -> str:
        return "\n".join(self.top)

    def bottom_text(self) -> str:
        return "\n".join(self.bottom)
