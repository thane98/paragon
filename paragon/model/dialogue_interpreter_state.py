import dataclasses
from typing import List

from paragon.model.dialogue_snapshot import DialogueSnapshot


@dataclasses.dataclass
class DialogueInterpreterState:
    avatar_config: object
    cur: DialogueSnapshot = dataclasses.field(default_factory=DialogueSnapshot)
    snapshots: List[DialogueSnapshot] = dataclasses.field(default_factory=list)

    def set_type(self, t):
        self.cur.conversation_type = t

    def set_active(self, active):
        self.commit()
        self.cur.set_active(active)
        self.cur.clear_text()

    def add_speaker(self, name, position):
        self.cur.add_speaker(name, position)

    def delete_speaker(self):
        self.cur.delete_speaker()

    def newline(self):
        self.cur.next_line()

    def clear(self):
        self.commit()
        self.cur.clear_text()

    def commit(self):
        if self.cur.has_text():
            self.snapshots.append(self.cur.clone())

    def append(self, message):
        if self.cur.is_end_of_message():
            self.commit()
        self.cur.append(message)

    def set_emotions(self, emotions):
        self.cur.set_emotions(emotions)

    def set_fid_alias(self, fid_alias):
        self.cur.set_fid_alias(fid_alias)

    def set_alias(self, alias):
        self.cur.set_alias(alias)

    def set_panicked(self, panicked):
        self.cur.panicked = panicked
