from paragon.core.services import utils
from paragon.core.services.chapters import Chapters
from paragon.model.chapter_data import ChapterData


class FE13Chapters(Chapters):
    def set_dirty(self, chapter_data: ChapterData, dirty: bool):
        if chapter_data.dispos_key:
            self.gd.multi_set_dirty("dispos", chapter_data.dispos_key, True)
        if chapter_data.terrain_key:
            self.gd.multi_set_dirty("grids", chapter_data.terrain_key, True)
        if chapter_data.person_key:
            self.gd.multi_set_dirty("person", chapter_data.person_key, True)
        if chapter_data.config_key:
            self.gd.multi_set_dirty("map_configs", chapter_data.config_key, True)
        if chapter_data.landscape_key:
            self.gd.multi_set_dirty("landscape", chapter_data.landscape_key, True)

    def _new(self, source: str, dest: str, **kwargs) -> ChapterData:
        # Get the source chapter declaration.
        source_decl = self.gd.key_to_rid("chapters", source)
        if not source_decl:
            raise KeyError(f"{source} is not a valid chapter.")

        # Create paths to every source file.
        source_part = source[4:] if source.startswith("CID_") else source
        dest_part = dest[4:] if dest.startswith("CID_") else dest
        source_dispos_path = f"data/dispos/{source_part}.bin.lz"
        source_person_path = f"data/person/{source_part}.bin.lz"
        source_landscape_path = f"data/landscape/{source_part}.bin.lz"
        source_terrain_path = f"data/terrain/{source_part}.bin.lz"
        source_config_path = f"map/data/{source_part}.bin"

        # Create paths to every dest file.
        dest_dispos_path = f"data/dispos/{dest_part}.bin.lz"
        dest_person_path = f"data/person/{dest_part}.bin.lz"
        dest_landscape_path = f"data/landscape/{dest_part}.bin.lz"
        dest_terrain_path = f"data/terrain/{dest_part}.bin.lz"
        dest_config_path = f"map/data/{dest_part}.bin"
        dest_dialogue_path = f"m/{dest_part}.bin.lz"

        # Duplicate source data to dest.
        dispos = utils.try_multi_duplicate(
            self.gd, "dispos", source_dispos_path, dest_dispos_path
        )
        person = utils.try_multi_duplicate(
            self.gd, "person", source_person_path, dest_person_path
        )
        landscape = utils.try_multi_duplicate(
            self.gd, "landscape", source_landscape_path, dest_landscape_path
        )
        terrain = utils.try_multi_duplicate(
            self.gd, "grids", source_terrain_path, dest_terrain_path
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
            landscape=landscape,
            landscape_key=dest_landscape_path if landscape else None,
            dialogue=dest_dialogue_path,
        )

    def _load(self, cid: str) -> ChapterData:
        # Validate that the CID corresponds to a chapter.
        cid_part = cid[4:] if cid.startswith("CID_") else cid
        decl = self.gd.key_to_rid("chapters", cid)
        if not decl:
            raise KeyError(f"{cid} is not a valid chapter.")

        # Create paths to every chapter file.
        # TODO: Dialogue!
        dispos_path = f"data/dispos/{cid_part}.bin.lz"
        person_path = f"data/person/{cid_part}.bin.lz"
        landscape_path = f"data/landscape/{cid_part}.bin.lz"
        terrain_path = f"data/terrain/{cid_part}.bin.lz"
        config_path = f"map/data/{cid_part}.bin"
        dialogue_path = f"m/{cid_part}.bin.lz"

        # Load chapter data.
        dispos = utils.try_multi_open(self.gd, "dispos", dispos_path)
        person = utils.try_multi_open(self.gd, "person", person_path)
        landscape = utils.try_multi_open(self.gd, "landscape", landscape_path)
        terrain = utils.try_multi_open(self.gd, "grids", terrain_path)
        config = utils.try_multi_open(self.gd, "map_configs", config_path)

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
            person=person,
            person_key=person_path if person else None,
            terrain=terrain,
            terrain_key=terrain_path if terrain else None,
            config=config,
            config_key=config_path if config else None,
            landscape=landscape,
            landscape_key=landscape_path if landscape else None,
            dialogue=dialogue_path,
        )
