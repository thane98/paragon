import os
from typing import Optional

from PySide2 import QtCore

from paragon.core.display import display_rid
from paragon.core.services import utils

from paragon.core.services.chapters import Chapters
from paragon.model.chapter_data import ChapterData
from paragon.model.fe14_chapter_route import FE14ChapterRoute


_HANDOVER_FILES = ["A_HANDOVER.bin.lz", "B_HANDOVER.bin.lz", "C_HANDOVER.bin.lz"]


class FE14Chapters(Chapters):
    def __init__(self, gd, models, icons):
        super().__init__(gd, models, icons)

        self.handovers = []
        keys = gd.multi_keys("person")
        for key in keys:
            for handover_file in _HANDOVER_FILES:
                if key.endswith(handover_file):
                    handover = utils.try_multi_open(gd, "person", key)
                    if handover:
                        self.handovers.append(handover)

    def pid_to_person(self, pid, person_key=None):
        if person_key:
            rid = self.gd.multi_open("person", person_key)
            if rid:
                if char_rid := self.gd.list_key_to_rid(rid, "people", pid):
                    return char_rid
        for handover in self.handovers:
            person = self.gd.list_key_to_rid(handover, "people", pid)
            if person:
                return person
        return self.gd.key_to_rid("characters", pid)

    def spawn_decoration(self, spawn, cid):
        pid = self.gd.string(spawn, "pid")
        if not pid:
            return None
        person = None
        chapter_data = self.load(cid)
        if chapter_data.person:
            person = self.gd.list_key_to_rid(chapter_data.person, "people", pid)
        if not person:
            for handover in self.handovers:
                person = self.gd.list_key_to_rid(handover, "people", pid)
                if person:
                    break
        if not person:
            person = self.gd.key_to_rid("characters", pid)
        if not person:
            return None
        army = self.gd.rid(person, "army")
        return self.icons.icon(army) if army else None

    def set_dirty(self, chapter_data: ChapterData, dirty: bool):
        if chapter_data.dispos_key:
            self.gd.multi_set_dirty("dispos", chapter_data.dispos_key, dirty)
        if chapter_data.terrain_key:
            self.gd.multi_set_dirty("terrain", chapter_data.terrain_key, dirty)
        if chapter_data.person_key:
            self.gd.multi_set_dirty("person", chapter_data.person_key, dirty)
        if chapter_data.config_key:
            self.gd.multi_set_dirty("map_configs", chapter_data.config_key, dirty)

    def terrain_to_colors(self, terrain_rid):
        tiles = self.gd.rid(terrain_rid, "tiles")
        tiles = self.gd.items(tiles, "tiles")
        grid_struct = self.gd.rid(terrain_rid, "grid")
        raw = self.gd.bytes(grid_struct, "grid")
        res = []
        for r in range(0, 32):
            colors = []
            for c in range(0, 32):
                b = raw[r * 32 + c]
                if b in range(0, len(tiles)):
                    colors.append(self.tile_to_color(tiles[b]))
            res.append(colors)
        return res

    def tiles_model(self, cid):
        data = self.load(cid)
        if not data.terrain:
            return None
        tiles_table = self.gd.rid(data.terrain, "tiles")
        if not tiles_table:
            return None
        return self.models.get(tiles_table, "tiles")

    def tile_name(self, terrain, cid, row, col) -> Optional[str]:
        model = self.tiles_model(cid)
        if not model:
            return None
        data = self.load(cid)
        grid = self.gd.rid(data.terrain, "grid")
        tile_id = self.gd.get_byte(grid, "grid", row * 32 + col)
        index = model.index(tile_id, 0)
        return model.data(index, QtCore.Qt.DisplayRole)

    def spawn_name(self, spawn, cid) -> Optional[str]:
        if not spawn or not cid:
            return None
        pid = self.gd.string(spawn, "pid")
        if not pid:
            return "{Missing PID}"
        chapter_data = self.load(cid)
        person = chapter_data.person
        if not person:
            return pid
        rid = self.gd.list_key_to_rid(person, "people", pid)
        if not rid:
            rid = self.gd.key_to_rid("characters", pid)
        if not rid:
            for handover in self.handovers:
                rid = self.gd.list_key_to_rid(handover, "people", pid)
                if rid:
                    break
        if not rid:
            return pid
        else:
            return display_rid(self.gd, rid, "fe14_character", None)

    def set_tile(self, terrain, tile, row, col):
        tiles = self.gd.rid(terrain, "tiles")
        grid = self.gd.rid(terrain, "grid")
        index = self.gd.list_index_of(tiles, "tiles", tile)
        if index:
            self.gd.set_byte(grid, "grid", row * 32 + col, index)
        else:
            raise KeyError("Tile is not in the tiles table.")

    def get_tile(self, terrain, row, col):
        tiles = self.gd.rid(terrain, "tiles")
        grid = self.gd.rid(terrain, "grid")
        index = self.gd.get_byte(grid, "grid", row * 32 + col)
        size = self.gd.list_size(tiles, "tiles")
        return 0 if index >= size else self.gd.list_get(tiles, "tiles", index)

    def _new(self, source: str, dest: str, **kwargs) -> ChapterData:
        # Get the source chapter declaration.
        source_decl = self.gd.key_to_rid("chapters", source)
        if not source_decl:
            raise KeyError(f"{source} is not a valid chapter.")

        # Get the source and destination routes.
        source_route = self._get_chapter_route(source_decl)
        dest_route = kwargs["route"]

        # Get source and dest filenames.
        source_part = source[4:] if source.startswith("CID_") else source
        source_base_name = source_part + ".bin"
        source_compressed_name = source_part + ".bin.lz"
        dest_part = dest[4:] if dest.startswith("CID_") else dest
        dest_base_name = dest_part + ".bin"
        dest_compressed_name = dest_part + ".bin.lz"

        # Create paths to every source file.
        source_dispos_path = os.path.join(
            "GameData", "Dispos", source_route.subdir(), source_compressed_name
        )
        source_person_path = os.path.join(
            "GameData", "Person", source_route.subdir(), source_compressed_name
        )
        source_terrain_path = os.path.join(
            "GameData", "Terrain", source_compressed_name
        )
        source_config_path = os.path.join("map", "config", source_base_name)

        # Create paths to every dest file.
        dest_dispos_path = os.path.join(
            "GameData", "Dispos", dest_route.subdir(), dest_compressed_name
        )
        dest_person_path = os.path.join(
            "GameData", "Person", dest_route.subdir(), dest_compressed_name
        )
        dest_terrain_path = os.path.join("GameData", "Terrain", dest_compressed_name)
        dest_config_path = os.path.join("map", "config", dest_base_name)
        dest_dialogue_path = os.path.join(
            "m", dest_route.subdir(), dest_compressed_name
        )

        # Duplicate source data to dest.
        dispos = utils.try_multi_duplicate(
            self.gd, "dispos", source_dispos_path, dest_dispos_path
        )
        person = utils.try_multi_duplicate(
            self.gd, "person", source_person_path, dest_person_path
        )
        terrain = utils.try_multi_duplicate(
            self.gd, "terrain", source_terrain_path, dest_terrain_path
        )
        config = utils.try_multi_duplicate(
            self.gd, "map_configs", source_config_path, dest_config_path
        )

        # Create text data for the chapter.
        self.gd.new_text_data(dest_dialogue_path, True)
        self.gd.set_message(dest_dialogue_path, True, "MID_Placeholder", "Placeholder")

        # Create a new chapter declaration.
        rid, field_id = self.gd.table("chapters")
        dest_decl = self.gd.list_add(rid, field_id)
        self.gd.copy(source_decl, dest_decl, [])
        self.gd.set_string(dest_decl, "cid", dest)

        # Return the resulting chapter data.
        return ChapterData(
            cid=dest,
            decl=dest_decl,
            dispos=dispos,
            dispos_key=dest_dispos_path if dispos else None,
            person=person,
            person_key=dest_person_path if person else None,
            terrain=terrain,
            terrain_key=dest_terrain_path if terrain else None,
            config=config,
            config_key=dest_config_path if config else None,
            dialogue=dest_dialogue_path,
            fe14_route=dest_route,
        )

    def _load(self, cid: str) -> ChapterData:
        # Validate that the CID corresponds to a chapter.
        cid_part = cid[4:] if cid.startswith("CID_") else cid
        decl = self.gd.key_to_rid("chapters", cid)
        if not decl:
            raise KeyError(f"{cid} is not a valid chapter.")

        # Get the chapter route.
        route = self._get_chapter_route(decl)
        if route == FE14ChapterRoute.INVALID:
            raise ValueError(f"Cannot determine route for chapter {cid}")

        base_name = cid_part + ".bin"
        compressed_name = cid_part + ".bin.lz"

        # Create paths to every chapter file.
        terrain_path = os.path.join("GameData", "Terrain", compressed_name)
        config_path = os.path.join("map", "config", base_name)
        dialogue_path_1 = os.path.join("m", route.subdir(), compressed_name)
        dialoge_path_2 = os.path.join("m", compressed_name)

        # Load chapter data.
        dispos, dispos_path = utils.try_open_fe14_route_file(
            self.gd,
            "dispos",
            os.path.join("GameData", "Dispos"),
            route.subdir(),
            compressed_name,
        )
        person, person_path = utils.try_open_fe14_route_file(
            self.gd,
            "person",
            os.path.join("GameData", "Person"),
            route.subdir(),
            compressed_name,
        )
        terrain = utils.try_multi_open(self.gd, "terrain", terrain_path)
        config = utils.try_multi_open(self.gd, "map_configs", config_path)

        # Load text data.
        try:
            # Try to open an existing text archive.
            self.gd.open_text_data(dialogue_path_1, True)
            dialogue_path = dialogue_path_1
        except:
            try:
                self.gd.open_text_data(dialoge_path_2, True)
                dialogue_path = dialoge_path_2
            except:
                dialogue_path = None

        return ChapterData(
            cid=cid,
            decl=decl,
            dispos=dispos,
            dispos_key=dispos_path if dispos else None,
            person=person,
            person_key=person_path if person else None,
            terrain=terrain,
            terrain_key=terrain_path if terrain else None,
            config=config,
            config_key=config_path if config else None,
            dialogue=dialogue_path,
            fe14_route=route,
        )

    def _get_chapter_route(self, chapter) -> FE14ChapterRoute:
        if not chapter:
            return FE14ChapterRoute.INVALID
        route = self.gd.int(chapter, "route")
        if route == 0b001:
            return FE14ChapterRoute.BIRTHRIGHT
        elif route == 0b010:
            return FE14ChapterRoute.CONQUEST
        elif route == 0b100:
            return FE14ChapterRoute.REVELATION
        else:
            return FE14ChapterRoute.ALL
