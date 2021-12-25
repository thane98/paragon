import os
from typing import Optional

from paragon.core.services.gc_portraits import GCPortraits
from paragon.model.portrait_info import PortraitInfo


class FE10Portraits(GCPortraits):
    def _character_to_job(self, rid: int) -> Optional[int]:
        pass

    def fsid_to_portrait_info(
        self, fsid: str, mode=None, **kwargs
    ) -> Optional[PortraitInfo]:
        rid = self.data.key_to_rid("portraits", fsid)
        if not rid:
            return None
        else:
            filename = self.data.string(rid, "file")
            if not filename:
                return None
            if mode == "mini":
                return PortraitInfo(
                    body_arc=filename,
                    file_index=-1,
                )
            else:
                file_index = 1 if mode == "big" else 0
                left_eye_x = self.data.int(rid, "big_portrait_left_eye_position_x")
                left_eye_y = self.data.int(rid, "big_portrait_left_eye_position_y")
                right_eye_x = self.data.int(rid, "big_portrait_right_eye_position_x")
                right_eye_y = self.data.int(rid, "big_portrait_right_eye_position_y")
                mouth_x = self.data.int(rid, "big_portrait_mouth_position_x")
                mouth_y = self.data.int(rid, "big_portrait_mouth_position_y")
                adjustment_x = self.data.int(rid, "small_portrait_adjustment_x")
                adjustment_y = self.data.int(rid, "small_portrait_adjustment_y")
                has_left_eye = left_eye_x != -1
                has_right_eye = right_eye_x != -1
                has_mouth = mouth_x != -1
                component_indices = self._get_component_indices(
                    has_left_eye, has_right_eye, has_mouth
                )
                if mode != "big":
                    left_eye_x -= adjustment_x
                    left_eye_y -= adjustment_y
                    right_eye_x -= adjustment_x
                    right_eye_y -= adjustment_y
                    mouth_x -= adjustment_x
                    mouth_y -= adjustment_y
                return PortraitInfo(
                    body_arc=filename,
                    draw_coords={
                        "left_eye": (left_eye_x, left_eye_y),
                        "right_eye": (right_eye_x, right_eye_y),
                        "mouth": (mouth_x, mouth_y),
                    },
                    component_indices=component_indices,
                    file_index=file_index,
                )

    def _get_component_indices(self, has_left_eye, has_right_eye, has_mouth):
        if has_left_eye and has_right_eye and has_mouth:
            return {
                "left_eye": 8,
                "right_eye": 11,
                "mouth_standard": 7,
                "mouth_happy": 5,
            }
        if not has_left_eye and not has_right_eye and has_mouth:
            return {
                "mouth_standard": 7,
                "mouth_happy": 5,
            }
        if has_left_eye and has_right_eye and not has_mouth:
            return {"left_eye": 3, "right_eye": 6}
        return {}

    def _read_portrait_arc(self, path: str):
        return self.data.read_tpl_textures(os.path.join("face", path))
