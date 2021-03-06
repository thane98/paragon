from PySide2 import QtCore

from paragon.ui.controllers.fe15_unit_sprite_item import FE15UnitSpriteItem
from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget

class FE15SpriteViewer(AbstractAutoWidget, FE15UnitSpriteItem):
    def __init__(self, state, spec):
        AbstractAutoWidget.__init__(self, state)
        FE15UnitSpriteItem.__init__(self, self.gs.sprites, self.gs.sprite_animation)
        self.setFixedSize(40, 40)
        self.rid = None
        self.service = self.gs.sprites
        self.team = 0
        self.new_animation.connect(self.draw_new_animation)
        self.reset_animation_to_idle.connect(self.idle_animation)
        self.left_clicked.connect(self._on_change_team)


    def set_target(self, rid):
        self.team = 0
        self.reset_animation()
        if rid:
            self.rid = rid
            self._load_sprite()

    def _on_change_team(self):
        if self.team < 2:
            self.team += 1
        else:
            self.team = 0

        if self.rid:
            self._load_sprite()

    @QtCore.Slot(int)
    def draw_new_animation(self, animation_index):
        fallback = self.data.string(self.rid, "aid")
        fallback = fallback[4:] if fallback else self.data.string(self.rid, "jid")[4:]
        jid = fallback
        self.sprite = self.service.load(None, jid, self.team, fallback_job=fallback, animation=animation_index)
        self.setPixmap(self.sprite.spritesheet) if self.sprite else self.setPixmap(None)
        self.current_frame.setX(0)
        self.current_frame.setY(0)
        self.frame_index = 0
        self.animation_index = animation_index
        self.next_frame()

    def idle_animation(self):
        if self.rid:
            fallback = self.data.string(self.rid, "aid")
            fallback = fallback[4:] if fallback else self.data.string(self.rid, "jid")[4:]
            jid = fallback
            self.sprite = self.service.load(None, jid, self.team, fallback_job=fallback)
            self.setPixmap(self.sprite.spritesheet) if self.sprite else self.setPixmap(None)
            self.animation_index = 0
            self.frame_index = 0
            self.current_frame.setX(0)
            self.current_frame.setY(0)
            self._reset_actions()

    def _load_sprite(self):
        fallback = self.data.string(self.rid, "aid")
        fallback = fallback[4:] if fallback else self.data.string(self.rid, "jid")[4:]
        jid = fallback
        self.set_sprite(
            self.service.load(None, jid, self.team, fallback_job=fallback)
        )
