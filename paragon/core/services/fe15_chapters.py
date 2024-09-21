from typing import Optional

from PySide6 import QtCore

from paragon.core import display
from paragon.core.services import utils
from paragon.core.services.chapters import Chapters
from paragon.model.chapter_data import ChapterData


class FE15Chapters(Chapters):
    def spawn_decoration(self, spawn, _):
        army = self.gd.rid(spawn, "army")
        return self.icons.icon(army) if army else None

    def tile_to_color(self, tile) -> Optional[str]:
        tid = self.gd.string(tile, "tid")
        if not tid:
            return None
        mtid = "M" + tid
        if mtid in self.tile_colors:
            return self.tile_colors[mtid]
        else:
            return self.default_tile_color()

    def terrain_to_colors(self, terrain_rid):
        rid, field_id = self.gd.table("tiles")
        tiles = self.gd.items(rid, field_id)
        raw = self.gd.bytes(terrain_rid, "grid")
        res = []
        for r in range(0, 32):
            colors = []
            for c in range(0, 32):
                b = raw[r * 32 + c]
                if b in range(0, len(tiles)):
                    colors.append(self.tile_to_color(tiles[b]))
            res.append(colors)
        return res

    def set_tile(self, terrain, tile, row, col):
        table_rid, field_id = self.gd.table("tiles")
        index = self.gd.list_index_of(table_rid, field_id, tile)
        if index:
            self.gd.set_byte(terrain, "grid", row * 32 + col, index)
        else:
            raise KeyError("Tile is not in the tiles table.")

    def get_tile(self, terrain, row, col):
        table_rid, field_id = self.gd.table("tiles")
        index = self.gd.get_byte(terrain, "grid", row * 32 + col)
        size = self.gd.list_size(table_rid, field_id)
        return 0 if index >= size else self.gd.list_get(table_rid, field_id, index)

    def tiles_model(self, cid):
        rid, field_id = self.gd.table("tiles")
        return self.models.get(rid, field_id)

    def tile_name(self, terrain, cid, row, col) -> Optional[str]:
        if not terrain:
            return None
        tile_id = self.gd.get_byte(terrain, "grid", row * 32 + col)
        model = self.tiles_model(cid)
        return model.data(model.index(tile_id, 0), QtCore.Qt.DisplayRole)

    def spawn_name(self, spawn, cid) -> Optional[str]:
        if not spawn:
            return None
        pid = self.gd.string(spawn, "pid")
        if not pid:
            return "{No PID}"
        character = self.gd.key_to_rid("characters", pid)
        if not character:
            return pid
        return display.display_fe15_character(self.gd, character, None)

    def set_dirty(self, chapter_data: ChapterData, dirty: bool):
        if chapter_data.dispos_key:
            self.gd.multi_set_dirty("dispos", chapter_data.dispos_key, dirty)
        if chapter_data.terrain_key:
            self.gd.multi_set_dirty("grids", chapter_data.terrain_key, dirty)

    def _new(self, source: str, dest: str, **kwargs) -> ChapterData:
        # Get the source chapter declaration.
        source_decl = self.gd.key_to_rid("chapters", source)
        if not source_decl:
            raise KeyError(f"{source} is not a valid chapter.")

        # Create paths to every source file.
        source_part = source[4:] if source.startswith("CID_") else source
        dest_part = dest[4:] if dest.startswith("CID_") else dest
        source_dispos_path = f"Data/Dispos/{source_part}.bin.lz"
        source_terrain_path = f"Data/Terrain/{source_part}.bin.lz"
        source_event_path = f"Data/Event/{source_part}.bin.lz"

        # Create paths to every dest file.
        dest_dispos_path = f"Data/Dispos/{dest_part}.bin.lz"
        dest_terrain_path = f"Data/Terrain/{dest_part}.bin.lz"
        dest_event_path = f"Data/Event/{dest_part}.bin.lz"
        dest_dialogue_path = f"m/{dest_part}.bin.lz"

        # Duplicate source data to dest.
        dispos = utils.try_multi_duplicate(
            self.gd, "dispos", source_dispos_path, dest_dispos_path
        )
        terrain = utils.try_multi_duplicate(
            self.gd, "grids", source_terrain_path, dest_terrain_path
        )
        event = utils.try_multi_duplicate(
            self.gd, "events", source_event_path, dest_event_path
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
            terrain=terrain,
            terrain_key=dest_terrain_path if terrain else None,
            event=event,
            event_key=dest_event_path if event else None,
            dialogue=dest_dialogue_path,
        )

    def _load(self, cid: str) -> ChapterData:
        # Validate that the CID corresponds to a chapter.
        cid_part = cid[4:] if cid.startswith("CID_") else cid
        decl = self.gd.key_to_rid("chapters", cid)
        if not decl:
            raise KeyError(f"{cid} is not a valid chapter.")

        # Create paths to every chapter file.
        dispos_path = f"Data/Dispos/{cid_part}.bin.lz"
        terrain_path = f"Data/Terrain/{cid_part}.bin.lz"
        event_path = f"Data/Event/{cid_part}.bin.lz"
        dialogue_path = f"m/{cid_part}.bin.lz"

        # Load chapter data.
        dispos = utils.try_multi_open(self.gd, "dispos", dispos_path)
        terrain = utils.try_multi_open(self.gd, "grids", terrain_path)
        event = utils.try_multi_open(self.gd, "events", event_path)

        # Load text data.
        try:
            # Try to open an existing text archive.
            self.gd.open_text_data(dialogue_path, True)
        except:
            dialogue_path = None

        return ChapterData(
            cid=cid,
            decl=decl,
            dispos=dispos,
            dispos_key=dispos_path if dispos else None,
            terrain=terrain,
            terrain_key=terrain_path if terrain else None,
            event=event,
            event_key=event_path if event else None,
            dialogue=dialogue_path,
        )

    def _get_script_path_from_cid(self, cid: str) -> str:
        return f"Scripts/{cid[4:]}"

    def _get_script_path_from_chapter_data(self, data: ChapterData) -> str:
        return f"Scripts/{data.cid[4:]}.cmb"
