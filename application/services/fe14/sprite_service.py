import logging
from typing import Dict, Optional

import fefeditor2
from PIL import Image
from PySide2.QtGui import QPixmap
from diskcache import Cache

from model.texture import Texture
from module.properties.property_container import PropertyContainer
from module.table_module import TableModule
from services.service_locator import locator

_AID_KEY = "AID"
_CLASS_KEY = "Class 1"
_JID_KEY = "JID"
_UNIQUE_FILE_TEMPLATE = "/unit/Unique/%s_%s/%s.bch.lz"
_HEAD_FILE_TEMPLATE = "/unit/Head/%s/%s.bch.lz"
_BODY_ANIME_TEMPLATE = "/unit/Body/%s/anime.bin"
_BODY_FILE_TEMPLATE = "/unit/Body/%s/%s.bch.lz"
_SPRITE_DIMENSION_KEY = "Size X of Head Sprite (2)"
_SPRITE_HEAD_POSITION_X_KEY = "Position X of Head Sprite (2)"
_SPRITE_HEAD_POSITION_Y_KEY = "Position Y of Head Sprite (2)"
_CACHE = Cache(directory="cache/fe14_sprites")


def get_sprite_file_name_from_team(team: int):
    if team == 1:
        return "赤0"
    if team == 2:
        return "緑0"
    if team == 3:
        return "紫0"
    return "青0"


class RelevantSpriteData:
    def __init__(self, entry: PropertyContainer):
        self.head_x = entry[_SPRITE_HEAD_POSITION_X_KEY].value
        self.head_y = entry[_SPRITE_HEAD_POSITION_Y_KEY].value
        self.is_half_size = entry[_SPRITE_DIMENSION_KEY].value == 16


class FE14SpriteService:
    def get_sprite_for_character(self, character: PropertyContainer, team: int) -> Optional[QPixmap]:
        assets_service = locator.get_scoped("AssetsService")
        class_module: TableModule = locator.get_scoped("ModuleService").get_module("Classes")
        sprite_file_name = get_sprite_file_name_from_team(team)
        class_id = character[_CLASS_KEY].value
        job = class_module.entries[class_id]
        jid = job[_JID_KEY].value
        aid = character[_AID_KEY].value
        if not aid:
            aid = jid

        unique_path = _UNIQUE_FILE_TEMPLATE % (jid[4:], aid[4:], sprite_file_name)
        head_dir_path = _HEAD_FILE_TEMPLATE % (aid[4:], sprite_file_name)
        body_dir_path = _BODY_FILE_TEMPLATE % (jid[4:], sprite_file_name)
        body_anime_path = _BODY_ANIME_TEMPLATE % jid[4:]

        if unique_path in _CACHE:
            return _CACHE[unique_path].toqpixmap()
        if head_dir_path + body_dir_path in _CACHE:
            return _CACHE[head_dir_path + body_dir_path].toqpixmap()

        unique_texture: Optional[Dict[str, Texture]] = assets_service.load_bch(unique_path)
        if unique_texture:
            result = self._assemble_unique_sprite(unique_texture["tmp"])
            if result:
                _CACHE[unique_path] = result
            return result.toqpixmap()
        head_texture: Optional[Dict[str, Texture]] = assets_service.load_bch(head_dir_path)
        if not head_texture:
            return None
        body_texture: Optional[Dict[str, Texture]] = assets_service.load_bch(body_dir_path)
        if not body_texture:
            return None

        relevant_sprite_data = self._load_sprite_data_from_anime(body_anime_path)
        result = self._assemble_sprite(head_texture["tmp"], body_texture["tmp"], relevant_sprite_data)
        if result:
            _CACHE[unique_path] = result
        return result.toqpixmap()

    @staticmethod
    def _assemble_unique_sprite(texture: Texture):
        try:
            raw_texture = texture.raw_image()
            cropped_texture = raw_texture.crop(box=(0, 32, 32, 64)).rotate(90)
            removed_transparency = fefeditor2.increase_alpha(cropped_texture.tobytes())
            return Image.frombytes("RGBA", (32, 32), removed_transparency, "raw", "RGBA")
        except:
            logging.exception("Failed to assemble unique sprite.")
            return None

    @staticmethod
    def _assemble_sprite(head_texture: Texture, body_texture: Texture, sprite_data: RelevantSpriteData):
        try:
            raw_head_texture = head_texture.raw_image()
            raw_body_texture = body_texture.raw_image()
            head_box = (16, 0, 32, 16) if sprite_data.is_half_size else (32, 0, 64, 32)
            cropped_body_texture = raw_body_texture.crop(box=(0, 32, 32, 64)).rotate(90)
            cropped_head_texture = raw_head_texture.crop(box=head_box).rotate(90)
            full_head_texture = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
            full_head_texture.paste(cropped_head_texture, (sprite_data.head_x, sprite_data.head_y))
            merged_pixel_data = fefeditor2.merge_images_and_increase_alpha(
                full_head_texture.tobytes(),
                cropped_body_texture.tobytes()
            )
            return Image.frombytes("RGBA", (32, 32), merged_pixel_data, "raw", "RGBA")
        except:
            logging.exception("Failed to assemble sprite.")
            return None

    @staticmethod
    def _load_sprite_data_from_anime(anime_path) -> RelevantSpriteData:
        common_module_service = locator.get_scoped("CommonModuleService")
        template = locator.get_scoped("ModuleService").get_common_module_template("Sprite Bin Data")
        module = common_module_service.open_common_module(template, anime_path)
        entry = module.entries[0]
        return RelevantSpriteData(entry)
