import json
import logging
from typing import Dict, Optional

from paragon.core.services import utils
from paragon.model.coordinate_change_type import CoordinateChangeType
from paragon.model.gcn_chapter_data import GcnChapterData, GcnMapData, GcnDisposData


class FE9Maps:
    def __init__(self, gd):
        self.gd = gd

        self.chapter_data: Dict[str, GcnChapterData] = {}

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

    def get_terrain_colors(self, chapter_data: GcnChapterData):
        tile_rid, tile_field = self.gd.table("terrain_data")
        key_to_rid = self.gd.key_to_rid_mapping(tile_rid, tile_field)
        res = []
        for r in range(0, chapter_data.map_data.height):
            colors = []
            for c in range(0, chapter_data.map_data.width):
                success = False
                if c < chapter_data.map_data.width:
                    tile_id = chapter_data.map_data.get_tile(
                        r * chapter_data.map_data.width + c
                    )
                    tile_rid = key_to_rid.get(tile_id)
                    if tile_rid:
                        tile_mt = self.gd.string(tile_rid, "name")
                        if tile_mt in self.tile_colors:
                            colors.append(self.tile_colors[tile_mt])
                            success = True
                if not success:
                    colors.append("#424242")
            res.append(colors)
        return res

    def tile_name(self, chapter_data: GcnChapterData, row, col) -> Optional[str]:
        if row < chapter_data.map_data.height and col < chapter_data.map_data.width:
            index = row * chapter_data.map_data.width + col
            tile_id = chapter_data.map_data.get_tile(index)
            if tile_id:
                tile_rid = self.gd.key_to_rid("terrain_data", tile_id)
                if tile_rid:
                    return self.gd.display(tile_rid)

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

    def spawn_decoration(self, spawn):
        return None

    def is_spawn(self, rid):
        return self.gd.type_of(rid) == "Spawn" if rid else False

    def is_difficulty(self, rid):
        return self.gd.type_of(rid) == "DispoFile" if rid else False

    def is_group(self, rid):
        return self.gd.type_of(rid) == "DispoGroup" if rid else False

    def is_tile(self, rid):
        return self.gd.type_of(rid) == "TerrainData" if rid else False

    @staticmethod
    def default_tile_color():
        return "#FF302C2E"

    def spawn_name(self, spawn) -> Optional[str]:
        if spawn:
            return self.gd.display(spawn)

    def load(self, zmap: str) -> GcnChapterData:
        logging.info(f"Loading zmap {zmap}")
        if data := self.chapter_data.get(zmap):
            return data
        map_data: GcnMapData = self.gd.load_gcn_map(zmap)
        dispos_path = f"zmap/{zmap}/dispos.cmp"
        dispos: GcnDisposData = GcnDisposData(
            common=utils.try_multi_open(self.gd, "dispos_c", dispos_path),
            normal=utils.try_multi_open(self.gd, "dispos_n", dispos_path),
            hard=utils.try_multi_open(self.gd, "dispos_h", dispos_path),
            maniac=utils.try_multi_open(self.gd, "dispos_m", dispos_path),
        )
        chapter_data = GcnChapterData(zmap, map_data, dispos)
        self.chapter_data[zmap] = chapter_data
        return chapter_data
