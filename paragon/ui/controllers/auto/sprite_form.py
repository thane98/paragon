from PySide2.QtWidgets import QComboBox, QHBoxLayout
from PySide2.QtCore import QRect, QSize, QModelIndex, QAbstractListModel, Qt
from PySide2.QtGui import QIcon

from paragon.ui.controllers.auto.abstract_auto_widget import AbstractAutoWidget
from paragon.ui.controllers.sprites import FE13UnitSpriteItem
from paragon.model.game import Game

class SpriteForm(AbstractAutoWidget, QHBoxLayout):
    def __init__(self, state, spec, field_id):
        AbstractAutoWidget.__init__(self, state)
        QHBoxLayout.__init__(self)
        self.combo_box = QComboBox()
        self.combo_box.setStyleSheet("combobox-popup: 0;")
        self.combo_box.currentIndexChanged.connect(self._on_edit)
        self.field_id = field_id
        self.rid = None

        if self.gs.project.game == Game.FE13:
            self.sprite_item = FE13UnitSpriteItem(self.gs.sprites)
            self.sprite_item.setFixedSize(40, 40)
            self.addWidget(self.sprite_item)

            job_rid, jobs = self.data.table("jobs")
            job = self.data.items(job_rid, jobs)

            for job_rid in job:
                jid = self.data.string(job_rid, "jid")
                localized_name = self.data.display(job_rid)
                localized_name = (
                    f"{localized_name} ♂" if jid.endswith("男") else
                    f"{localized_name} ♀" if jid.endswith("女") else
                    localized_name
                )
                self.combo_box.addItem(localized_name, jid)

        self.addWidget(self.combo_box)

    def set_target(self, rid):
        self.sprite_item.reset_animation()
        self.rid = rid
        self.sprites = list()
        job_rid, jobs = self.data.table("jobs")
        job = self.data.items(job_rid, jobs)

        if self.rid:
            for job_rid in job:
                bmap_icon = self.data.rid(job_rid, "bmap_icon")
                if bmap_icon:
                    bmap_name = self.data.string(bmap_icon, "name")
                    fallback = bmap_name
                    name = self.data.display(job_rid)
                    jid = self.data.string(job_rid, "jid")
                    pid = self.data.string(self.rid, "pid")

                    bmap_name = bmap_name[:-1] if bmap_name and (bmap_name.endswith("男") or bmap_name.endswith("女")) else bmap_name
                    pid = pid[4:] if pid and pid.startswith("PID_") else pid

                    sprite = self.gs.sprites._load(pid, bmap_name, "青", fallback)
                    self.sprites.append(sprite)

            job_rid = self.data.rid(self.rid, self.field_id)

            if job_rid:
                jid = self.data.string(job_rid, "jid")
                index = self.combo_box.findData(jid)
                if index in range(0, self.combo_box.model().rowCount()):
                    self.combo_box.setCurrentIndex(index)
                    self.sprite_item.set_sprite(self.sprites[index])
                else:
                    self.combo_box.setCurrentIndex(0)
                    self.sprite_item.set_sprite(self.sprites[0])
            else:
                self.combo_box.setCurrentIndex(-1)
                if self.sprite_item:
                    self.sprite_item.set_sprite(None)
        else:
            self.combo_box.setCurrentIndex(-1)
            if self.sprite_item:
                self.sprite_item.set_sprite(None)

        self.combo_box.setEnabled(self.rid is not None)

    def _on_edit(self):
        if self.rid and self.combo_box.currentIndex() >= 0:
            job_rid = self.data.rid(self.rid, self.field_id)
            self.data.set_string(job_rid, "jid", self.combo_box.currentData(Qt.UserRole))
            self.sprite_item.set_sprite(self.sprites[self.combo_box.currentIndex()])
