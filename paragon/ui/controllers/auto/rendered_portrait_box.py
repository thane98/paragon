from PySide2.QtWidgets import QGraphicsScene

from paragon.ui.controllers.auto.mini_portrait_box import MiniPortraitBox


class RenderedPortraitBox(MiniPortraitBox):
    def _retrieve(self, rid):
        if not rid:
            return None
        elif self.spec.retrieve_mode == "character":
            fid = self.service.character_to_fid(rid)
        elif self.spec.retrieve_mode == "class":
            return self.service.job_to_fid(rid)
        else:
            raise NotImplementedError
        return self.service.render(fid, [], self.spec.mode)

    def set_target(self, rid):
        texture = self._retrieve(rid)
        if not texture:
            self.setScene(QGraphicsScene())
        else:
            self.set_to_pixmap(texture)
