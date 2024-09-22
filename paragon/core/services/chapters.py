import json
import logging
import os.path
from pathlib import Path
from typing import Optional

from paragon.model.coordinate_change_type import CoordinateChangeType
from paragon.model.chapter_data import ChapterData
from paragon.model.exalt_script_model import ExaltScriptModel


class Chapters:
    def __init__(self, gd, models, icons):
        self.gd = gd
        self.chapters = {}
        self.models = models
        self.icons = icons

        tile_palette_path = "resources/misc/TilePalette.json"
        try:
            with open(tile_palette_path, "r", encoding="utf-8") as f:
                tile_palette = json.load(f)
        except:
            logging.exception("Failed to load tile colors.")
            self.tile_palette = {}

        tile_colors_path = "resources/misc/TileColors.json"
        self.tile_colors = {}
        try:
            with open(tile_colors_path, "r", encoding="utf-8") as f:
                tile_colors = json.load(f)
            for k in tile_colors:
                v = tile_colors[k]
                if v in tile_palette:
                    self.tile_colors[k] = tile_palette[v]
        except:
            logging.exception("Failed to load tile colors.")

    def spawn_decoration(self, spawn, cid):
        return None

    def coord(self, spawn, coord_2):
        field_id = "coord_2" if coord_2 else "coord_1"
        return list(self.gd.bytes(spawn, field_id))

    def move_spawn(self, spawn, row, col, coordinate_change_type: CoordinateChangeType):
        x, y = col, row
        if coordinate_change_type == CoordinateChangeType.BOTH:
            self.gd.set_bytes(spawn, "coord_1", [x, y])
            self.gd.set_bytes(spawn, "coord_2", [x, y])
        else:
            self.gd.set_bytes(spawn, coordinate_change_type.value, [x, y])

    def is_spawn(self, rid):
        return self.gd.type_of(rid) == "Spawn" if rid else False

    def is_faction(self, rid):
        return self.gd.type_of(rid) == "Faction" if rid else False

    def is_tile(self, rid):
        return self.gd.type_of(rid) == "Tile" if rid else False

    @staticmethod
    def default_tile_color():
        return "#FF302C2E"

    def terrain_to_colors(self, terrain_rid):
        raise NotImplementedError

    def tiles_model(self, cid):
        raise NotImplementedError

    def tile_name(self, terrain, cid, row, col) -> Optional[str]:
        raise NotImplementedError

    def spawn_name(self, spawn, cid) -> Optional[str]:
        raise NotImplementedError

    def set_tile(self, terrain, tile, row, col):
        raise NotImplementedError

    def get_tile(self, terrain, row, col):
        raise NotImplementedError

    def tile_to_color(self, tile) -> Optional[str]:
        mtid = self.gd.string(tile, "name")
        if mtid in self.tile_colors:
            return self.tile_colors[mtid]
        else:
            return self.default_tile_color()

    def validate_cid_for_new_chapter(self, cid):
        if not cid.startswith("CID_"):
            raise ValueError("Chapter CID must start with 'CID_'")
        if self.cid_in_use(cid):
            raise ValueError(
                f"CID '{cid}' is already used by a different chapter. Please enter a unique CID."
            )

    def cid_in_use(self, cid: str) -> bool:
        rid, field_id = self.gd.table("chapters")
        for chapter in self.gd.items(rid, field_id):
            if self.gd.key(chapter) == cid:
                return True
        return False

    def set_dirty(self, chapter_data: ChapterData, dirty: bool):
        raise NotImplementedError

    def load(self, cid: str) -> ChapterData:
        if cid in self.chapters:
            return self.chapters[cid]
        else:
            data = self._load(cid)
            self.chapters[cid] = data
            return data

    def new(
        self, source: str, dest: str, scripts_model: ExaltScriptModel = None, **kwargs
    ) -> ChapterData:
        # Verify that the dest CID is not overwriting something.
        if self.cid_in_use(dest):
            raise KeyError(f"Cannot overwrite {dest} with a new chapter.")
        data = self._new(source, dest, **kwargs)
        if scripts_model:
            source_path = self._get_script_path_from_cid(source).replace(
                "/", os.path.sep
            )
            dest_path = self._get_script_path_from_chapter_data(data).replace(
                "/", os.path.sep
            )
            parent_path = (
                Path("exalt/scripts")
                .joinpath(Path(*Path(source_path).parts[1:]))
                .with_suffix(".exl")
            )
            source_script_index = scripts_model.index_of(
                str(parent_path), "compile_target"
            )
            if source_script_index and source_script_index.isValid():
                script_data = scripts_model.data_at(source_script_index)
                if script_data:
                    source_node = script_data.node
                    text = self.gd.open_script(source_node)
                    dest_node = scripts_model.add_new_script_from_path(
                        str(Path(*Path(dest_path).parts[1:]))
                    )
                    if dest_node:
                        self.gd.update_script(dest_node, text)
        self.chapters[dest] = data
        return data

    def _get_script_path_from_cid(self, cid: str) -> str:
        raise NotImplementedError

    def _get_script_path_from_chapter_data(self, data: ChapterData) -> str:
        raise NotImplementedError

    def _new(self, source: str, dest: str, **kwargs) -> ChapterData:
        raise NotImplementedError

    def _load(self, cid: str) -> ChapterData:
        raise NotImplementedError
