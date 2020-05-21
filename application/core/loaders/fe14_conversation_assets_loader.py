from typing import Dict, List, Optional

from PySide2.QtGui import QPixmap, QImage

from services.service_locator import locator

_TALK_WINDOW_TYPE_0_DIMENSIONS = (384, 56)
_TALK_WINDOW_TYPE_1_DIMENSIONS = (406, 72)
_TALK_WINDOW_TYPE_2_DIMENSIONS = (200, 56)
_NAME_PLATE_DIMENSIONS = (112, 24)
_ARROW_DIMENSIONS = (16, 16)


def _slice_talk_window(talk_window: QPixmap) -> List[QPixmap]:
    type_0_width, type_0_height = _TALK_WINDOW_TYPE_0_DIMENSIONS
    type_0_pixmap = talk_window.copy(0, 0, type_0_width, type_0_height)
    type_1_width, type_1_height = _TALK_WINDOW_TYPE_1_DIMENSIONS
    type_1_pixmap = talk_window.copy(0, type_0_height, type_1_width, type_1_height)
    type_2_width, type_2_height = _TALK_WINDOW_TYPE_2_DIMENSIONS
    type_2_pixmap = talk_window.copy(0, type_0_height + type_1_height, type_2_width, type_2_height)
    return [type_0_pixmap, type_1_pixmap, type_2_pixmap]


def _slice_name_plate(name_plate_texture: QPixmap) -> Dict[str, QPixmap]:
    name_plate_width, name_plate_height = _NAME_PLATE_DIMENSIONS
    name_plate_pixmap = name_plate_texture.copy(0, 0, name_plate_width, name_plate_height)
    arrow_width, arrow_height = _ARROW_DIMENSIONS
    arrow_pixmap = name_plate_texture.copy(name_plate_width, 0, arrow_width, arrow_height)
    return {
        "plate": name_plate_pixmap,
        "arrow": arrow_pixmap
    }


class FE14ConversationAssetsLoader:
    @staticmethod
    def load_background() -> Optional[QPixmap]:
        assets_service = locator.get_scoped("AssetsService")
        arc = assets_service.load_arc("/effect/Tlp_Ev_t001.arc.lz")
        if not arc or "model.bch" not in arc:
            return None
        image: QImage = arc["model.bch"].image()
        return QPixmap.fromImage(image).copy(56, 8, 400, 240)

    @staticmethod
    def load_talk_windows() -> Dict:
        assets_service = locator.get_scoped("AssetsService")
        bch_talk_window_standard = assets_service.load_bch("/ui/TalkWindow.bch.lz")
        bch_name_plate = assets_service.load_bch("/ui/TalkWindow2.bch.lz")
        bch_talk_window_w = assets_service.load_bch("/ui/TalkWindowW.bch.lz")
        bch_talk_window_b = assets_service.load_bch("/ui/TalkWindowW.bch.lz")
        return {
            "standard": _slice_talk_window(QPixmap.fromImage(bch_talk_window_standard["TalkWindow"].image())),
            "name_plate": _slice_name_plate(QPixmap.fromImage(bch_name_plate["TalkWindow2"].image())),
            "birthright": _slice_talk_window(QPixmap.fromImage(bch_talk_window_w["TalkWindow"].image())),
            "conquest": _slice_talk_window(QPixmap.fromImage(bch_talk_window_b["TalkWindow"].image()))
        }