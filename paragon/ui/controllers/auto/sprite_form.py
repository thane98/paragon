from PySide2 import QtCore
from PySide2.QtWidgets import QComboBox, QHBoxLayout, QWidget

from paragon.model.game import Game
from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget
from paragon.ui.controllers.fe13_unit_sprite_item import FE13UnitSpriteItem
from paragon.ui.controllers.fe14_unit_sprite_item import FE14UnitSpriteItem
from paragon.ui.controllers.fe15_unit_sprite_item import FE15UnitSpriteItem
from paragon.ui.controllers.auto.reference_widget import ReferenceWidget


class SpriteForm(AbstractAutoWidget, QWidget):
    def __init__(self, state, spec, field_id):
        AbstractAutoWidget.__init__(self, state)
        QWidget.__init__(self)

        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)

        self.service = self.gs.sprites
        self.reference_widget = ReferenceWidget(state, spec, field_id)

        self.reference_widget.currentIndexChanged.connect(self._on_edit)
        self.field_id = field_id
        self.rid = None
        self.team = 0

        if self.gs.project.game == Game.FE13:
            self.sprite_item = FE13UnitSpriteItem(
                self.gs.sprites, self.gs.sprite_animation
            )
            self.sprite_item.setFixedSize(40, 40)
            layout.addWidget(self.sprite_item)
            self.sprite_item.left_clicked.connect(self._on_change_team)
        elif self.gs.project.game in Game.FE14:
            self.sprite_item = FE14UnitSpriteItem(
                self.gs.sprites, self.gs.sprite_animation
            )
            self.sprite_item.setFixedSize(40, 40)
            self.sprite_item.new_animation.connect(self.draw_new_animation)
            self.sprite_item.reset_animation_to_idle.connect(self.idle_animation)
            self.sprite_item.left_clicked.connect(self._on_change_team)
            layout.addWidget(self.sprite_item)
        elif self.gs.project.game in Game.FE15:
            self.sprite_item = FE15UnitSpriteItem(
                self.gs.sprites, self.gs.sprite_animation
            )
            self.sprite_item.setFixedSize(40, 40)
            self.sprite_item.new_animation.connect(self.draw_new_animation)
            self.sprite_item.reset_animation_to_idle.connect(self.idle_animation)
            self.sprite_item.left_clicked.connect(self._on_change_team)
            layout.addWidget(self.sprite_item)

        layout.addWidget(self.reference_widget)

    def set_target(self, rid):
        self.rid = rid
        self.team = 0
        self.sprite_item.reset_animation()

        self.reference_widget.set_target(self.rid)
        if self.rid:
            struct_rid = self.data.rid(self.rid, self.field_id)

            if struct_rid:
                if self.reference_widget.currentIndex() in range(
                    0, self.reference_widget.model().rowCount()
                ):
                    self._load_sprite(struct_rid)
            else:
                self.reference_widget.setCurrentIndex(-1)
                if self.sprite_item:
                    self.sprite_item.set_sprite(None)
        else:
            self.sprite_item.set_sprite(None)

    def _on_edit(self):
        if self.rid and self.reference_widget.currentIndex() >= 0:
            self._load_sprite(self.data.rid(self.rid, self.field_id))

    def _on_change_team(self):
        if self.gs.project.game == Game.FE13:
            if self.team < 2:
                self.team += 1
            else:
                self.team = 0
        elif self.gs.project.game == Game.FE14:
            if self.team < 3:
                self.team += 1
            else:
                self.team = 0
        elif self.gs.project.game == Game.FE15:
            if self.team < 2:
                self.team += 1
            else:
                self.team = 0

        if self.rid:
            struct_rid = self.data.rid(self.rid, self.field_id)

            if struct_rid:
                if self.reference_widget.currentIndex() in range(
                    0, self.reference_widget.model().rowCount()
                ):
                    self._load_sprite(struct_rid)

    def _load_sprite(self, struct_rid):
        struct_type = self.data.type_of(struct_rid)
        con_type = self.data.type_of(self.rid)
        if self.gs.project.game == Game.FE13:
            if struct_type == "BMapIcon":
                bmap_icon_name = self.data.string(struct_rid, "name")
                self.sprite_item.set_sprite(
                    self.service.load(
                        None, None, self.team, fallback_job=bmap_icon_name
                    )
                )
            elif struct_type == "Job":
                pid = self.data.string(self.rid, "pid")[4:]
                bmap_icon_rid = self.data.rid(struct_rid, "bmap_icon")
                fallback = self.data.string(bmap_icon_rid, "name")
                jid = fallback[:-1]
                self.sprite_item.set_sprite(
                    self.service.load(pid, jid, self.team, fallback_job=fallback)
                )
        elif self.gs.project.game == Game.FE14:
            fallback = self.data.string(struct_rid, "jid")[4:]
            jid = fallback
            if con_type == "Person":
                char = self.service.person_to_identifier(self.rid)
            else:
                char = jid
            self.sprite_item.set_sprite(
                self.service.load(char, jid, self.team, fallback_job=fallback)
            )
        elif self.gs.project.game == Game.FE15:
            char = (
                self.service.person_to_identifier(self.rid)
                if self.data.type_of(self.rid) == "Person"
                else None
                if self.data.type_of(self.rid) == "Job"
                else None
            )
            fallback = self.data.string(struct_rid, "aid")
            fallback = (
                fallback[4:] if fallback else self.data.string(struct_rid, "jid")[4:]
            )
            jid = fallback
            self.sprite_item.set_sprite(
                self.service.load(char, jid, self.team, fallback_job=fallback)
            )

    def idle_animation(self):
        if self.rid:
            struct_rid = self.data.rid(self.rid, self.field_id)
            if struct_rid:
                if self.gs.project.game in Game.FE14:
                    fallback = self.data.string(struct_rid, "jid")[4:]
                    jid = fallback
                    char = self.service.person_to_identifier(self.rid)
                    if not char:
                        char = jid
                elif self.gs.project.game in Game.FE15:
                    char = (
                        self.service.person_to_identifier(self.rid)
                        if self.data.type_of(self.rid) == "Person"
                        else None
                        if self.data.type_of(self.rid) == "Job"
                        else None
                    )
                    fallback = self.data.string(struct_rid, "aid")
                    fallback = (
                        fallback[4:]
                        if fallback
                        else self.data.string(struct_rid, "jid")[4:]
                    )
                    jid = fallback

                self.sprite_item.sprite = self.service.load(
                    char, jid, self.team, fallback_job=fallback
                )
                self.sprite_item.setPixmap(
                    self.sprite_item.sprite.spritesheet
                ) if self.sprite_item.sprite else self.sprite_item.setPixmap(None)
                self.sprite_item.animation_index = 0
                self.sprite_item.frame_index = 0
                self.sprite_item.current_frame.setX(0)
                self.sprite_item.current_frame.setY(0)
                self.sprite_item._reset_actions()

    def draw_new_animation(self, animation_index):
        struct_rid = self.data.rid(self.rid, self.field_id)
        if self.gs.project.game in Game.FE14:
            fallback = self.data.string(struct_rid, "jid")[4:]
            jid = fallback
            char = self.service.person_to_identifier(self.rid)
            if not char:
                char = jid
        elif self.gs.project.game in Game.FE15:
            char = (
                self.service.person_to_identifier(self.rid)
                if self.data.type_of(self.rid) == "Person"
                else None
                if self.data.type_of(self.rid) == "Job"
                else None
            )
            fallback = self.data.string(struct_rid, "aid")
            fallback = (
                fallback[4:] if fallback else self.data.string(struct_rid, "jid")[4:]
            )
            jid = fallback

        self.sprite_item.sprite = self.service.load(
            char, jid, self.team, fallback_job=fallback, animation=animation_index
        )
        self.sprite_item.setPixmap(
            self.sprite_item.sprite.spritesheet
        ) if self.sprite_item.sprite else self.sprite_item.setPixmap(None)
        self.sprite_item.current_frame.setX(0)
        self.sprite_item.current_frame.setY(0)
        self.sprite_item.frame_index = 0
        self.sprite_item.animation_index = animation_index
        self.sprite_item.next_frame()
