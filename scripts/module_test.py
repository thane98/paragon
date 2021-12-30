import os
import shutil
import sys
import tempfile
import traceback

from paragon.core.services.fe15_events import FE15Events
from paragon.model.fe14_chapter_route import FE14ChapterRoute

from paragon.core.services.fe13_chapters import FE13Chapters

from paragon import paragon as pgn
from paragon.core.services.fe14_chapters import FE14Chapters


rom_root = None
output_root = None
gd = None


def accuracy_test(path_in_rom, path_in_output, compressed):
    global rom_root
    global output_root
    original_path = os.path.join(rom_root, path_in_rom)
    new_path = os.path.join(output_root, path_in_output)
    with open(original_path, "rb") as f:
        original = f.read()
    with open(new_path, "rb") as f:
        new = f.read()
    if compressed:
        original = pgn.decompress_lz13(original)
        new = pgn.decompress_lz13(new)
    if original != new:
        print("FAILURE! Files do not match.")
    else:
        print("Success.")


def basic_test(store_id, path_in_rom, compressed=True):
    print(
        f"Testing accuracy for '{store_id}' with output path '{path_in_rom}'... ",
        end="",
    )
    global gd
    try:
        gd.set_store_dirty(store_id, True)
        gd.write()
        accuracy_test(path_in_rom, path_in_rom, compressed)
    except:
        print("FAILURE! Encountered exception:")
        traceback.print_exc()
    gd.set_store_dirty(store_id, False)


def multi_test(multi_id, path_in_rom, compressed=True):
    print(
        f"Testing accuracy for multi '{multi_id}' with output path '{path_in_rom}'... ",
        end="",
    )
    global gd
    try:
        gd.multi_open(multi_id, path_in_rom)
        gd.multi_set_dirty(multi_id, path_in_rom, True)
        gd.write()
        accuracy_test(path_in_rom, path_in_rom, compressed)
    except:
        print("FAILURE! Encountered exception:")
        traceback.print_exc()
    gd.multi_set_dirty(multi_id, path_in_rom, False)


def fe10_data_only_test(store, path, cutoff):
    print(f"Testing partial accuracy for {store}... ", end="")
    global gd
    try:
        gd.set_store_dirty(store, True)
        gd.write()
        pgn.compare_fe10data(
            os.path.join(rom_root, path), os.path.join(output_root, path), cutoff
        )
        print("Success.")
    except:
        print("FAILURE! Encountered exception:")
        traceback.print_exc()
    gd.set_store_dirty(store, False)


def awakening_new_chapter_test():
    print("Testing accuracy for creating a new chapter...")
    global gd
    try:
        chapters = FE13Chapters(gd, None, None)
        data = chapters.new("CID_X001", "CID_TEST")
        chapters.set_dirty(data, True)
        gd.write()
        print("\tDispos...", end="")
        accuracy_test("data/dispos/X001.bin.lz", "data/dispos/TEST.bin.lz", True)
        print("\tPerson...", end="")
        accuracy_test("data/person/X001.bin.lz", "data/person/TEST.bin.lz", True)
        print("\tGrids...", end="")
        accuracy_test("data/terrain/X001.bin.lz", "data/terrain/TEST.bin.lz", True)
        print("\tLandscape...", end="")
        accuracy_test("data/landscape/X001.bin.lz", "data/landscape/TEST.bin.lz", True)
        print("\tMap Config...", end="")
        accuracy_test("map/data/X001.bin", "map/data/TEST.bin", False)
        chapters.set_dirty(data, False)
    except:
        print("FAILURE! Encountered exception:")
        traceback.print_exc()


def awakening_gamedata_test():
    print("Testing accuracy for GameData ignoring ItemDataNum address... ", end="")
    global gd
    global rom_root
    global output_root
    try:
        gd.set_store_dirty("gamedata", True)
        gd.write()
        original_path = os.path.join(rom_root, "data/GameData.bin.lz")
        new_path = os.path.join(output_root, "data/GameData.bin.lz")
        original = pgn.load_awakening_gamedata_for_tests(original_path)
        new = pgn.load_awakening_gamedata_for_tests(new_path)
        if original != new:
            print("FAILURE! Files do not match.")
        else:
            print("Success.")
    except:
        print("FAILURE! Encountered exception:")
        traceback.print_exc()
    gd.set_store_dirty("gamedata", False)


def fates_gamedata_test():
    print("Testing accuracy for GameData by comparing regions...", end="")
    global gd
    global rom_root
    global output_root
    try:
        gd.set_store_dirty("gamedata", True)
        gd.write()
        original_path = os.path.join(rom_root, "GameData/GameData.bin.lz")
        new_path = os.path.join(output_root, "GameData/GameData.bin.lz")
        pgn.compare_fe14_gamedatas(
            original_path,
            new_path,
            [
                (0, 0, 0x64),
                (0x64, 0x64, 42196),  # Chapter table + character table.
                (0xADD0, 0xE0FC, 0x3C18),  # Supports.
                (0xE9E8, 0x11D14, 66720),  # Everything else.
            ],
        )
        print("Success.")
    except:
        print("FAILURE! Encountered exception:")
        traceback.print_exc()
    gd.set_store_dirty("gamedata", False)


def fates_new_chapter_test():
    print(f"Testing accuracy for creating a new chapter...")
    global gd
    try:
        chapters = FE14Chapters(gd, None, None)
        data = chapters.new("CID_B015", "CID_TEST", route=FE14ChapterRoute.BIRTHRIGHT)
        chapters.set_dirty(data, True)
        gd.write()
        print("\tDispos...", end="")
        accuracy_test(
            "GameData/Dispos/B/B015.bin.lz", "GameData/Dispos/A/TEST.bin.lz", True
        )
        print("\tTerrain...", end="")
        accuracy_test(
            "GameData/Terrain/B015.bin.lz", "GameData/Terrain/TEST.bin.lz", True
        )
        print("\tMap Config...", end="")
        accuracy_test("map/config/B015.bin", "map/config/TEST.bin", False)
        chapters.set_dirty(data, False)
    except:
        print("FAILURE! Encountered exception:")
        traceback.print_exc()


def fe15_event_compile_test():
    global gd
    events = FE15Events(gd)
    all_keys = gd.multi_keys("events")
    for key in all_keys:
        try:
            print(
                f"Testing accuracy for compiling and decompiling events in {key}...",
                end="",
            )
            rid = gd.multi_open("events", key)
            decls = gd.items(rid, "declarations")
            for decl in decls:
                event_table_header = gd.rid(decl, "events")
                event_table = gd.rid(event_table_header, "table")
                script = events.convert_to_paragon_event_script(event_table)
                events.convert_to_game_events(script, event_table)
            gd.multi_set_dirty("events", key, True)
            gd.write()
            accuracy_test(key, key, True)
            gd.multi_set_dirty("events", key, False)
        except:
            print("FAILURE! Encountered exception:")
            traceback.print_exc()


def test_fe10():
    fe10_data_only_test("fe10data", "FE10Data.cms", 0x279F8)
    fe10_data_only_test("fe10effect", "FE10Effect.cms", 0x3C10)
    fe10_data_only_test("fe10conversation", "FE10Conversation.cms", 0x10E54)
    fe10_data_only_test("sound_data_us", "Sound/sound_data_en.cms", 0x25038)
    fe10_data_only_test("fe10intro", "FE10Intro.bin", 0x1100)
    basic_test("facedata", "Face/facedata.bin")
    basic_test("shop_item_normal", "Shop/shopitem_n.bin")
    basic_test("shop_item_hard", "Shop/shopitem_h.bin")
    basic_test("shop_item_maniac", "Shop/shopitem_m.bin")
    basic_test("fe10epilogue", "FE10Epilogue.bin")
    multi_test("dispos", "zmap/bmap0000/dispos_c.bin")
    multi_test("dispos", "zmap/bmap0000/dispos_h.bin")
    multi_test("dispos", "zmap/bmap0000/dispos_n.bin")
    multi_test("dispos", "zmap/debug/dispos_c.bin")
    multi_test("dispos", "zmap/test_taisen01/dispos_c.bin")
    multi_test("dispos", "zmap/test_taisen01/dispos_n.bin")


def test_fe13():
    awakening_gamedata_test()
    basic_test("portraits", "face/FaceData.bin.lz")
    basic_test("characters", "data/person/static.bin.lz")
    basic_test("combotbl", "bs/ComboTbl.bin.lz")
    basic_test("combotbl_presets", "bs/Presets.bin.lz")
    basic_test("otherdata", "data/OtherData.bin.lz")
    # basic_test("reliance_list", "data/RelianceList.bin.lz")
    multi_test("grids", "data/terrain/000.bin.lz")
    multi_test("grids", "data/terrain/X005.bin.lz")
    multi_test("dispos", "data/dispos/000.bin.lz")
    multi_test("dispos", "data/dispos/X003.bin.lz")
    multi_test("map_configs", "map/data/000.bin", compressed=False)
    multi_test("map_configs", "map/data/007.bin", compressed=False)
    multi_test("landscape", "data/landscape/023.bin.lz", compressed=True)
    multi_test("landscape", "data/landscape/X021.bin.lz", compressed=True)
    if language == "EnglishNA":
        basic_test("indirect_sound_english", "sound/IndirectSound_US_EN.bin.lz")
        basic_test("indirect_sound_japanese_us", "sound/IndirectSound_US_JP.bin.lz")
    awakening_new_chapter_test()


def test_fe14():
    fates_gamedata_test()
    basic_test("indirect_sound", "sound/IndirectSound.bin.lz")
    basic_test("castle_person", "castle/CastlePerson.bin", compressed=False)
    basic_test("castle_join", "castle/castle_join.bin.lz")
    basic_test("castle_building", "castle/castle_building.bin.lz")
    basic_test("castle_init_buildings", "castle/castle_init_buildings.bin.lz")
    basic_test("game_effect", "GameData/GameEffect.bin.lz")
    basic_test("accessories", "GameData/AcceShop.bin.lz")
    basic_test("facedata", "face/FaceData.bin.lz")
    basic_test("rom0", "asset/ROM0.lz")
    basic_test("rom1", "asset/ROM1.lz")
    basic_test("rom2", "asset/ROM2.lz")
    basic_test("rom3", "asset/ROM3.lz")
    basic_test("rom4", "asset/ROM4.lz")
    basic_test("rom5", "asset/ROM5.lz")
    basic_test("rom6", "asset/ROM6.lz")
    basic_test("aset", "bs/aset.lz")
    basic_test("camera_data", "GameData/CameraData.bin.lz")
    basic_test("butler", "GameData/Castle/Butler.bin.lz")
    basic_test("dining_data", "GameData/Castle/DiningData.bin.lz")
    basic_test("geoattr", "GameData/GeoAttr.bin.lz")
    basic_test("reliance_bgm", "talk/RelianceTalkBGM.bin", compressed=False)
    basic_test("castle_position", "castle/CastlePosition.bin", compressed=False)
    basic_test("castle_butler_voice", "castle/CastleButlerVoice.bin", compressed=False)
    # basic_test("texture_coordinate", "TextureCoordinate.bin", compressed=False)
    multi_test("map_configs", "map/config/A000.bin", compressed=False)
    multi_test("map_configs", "map/config/B028.bin", compressed=False)
    multi_test("terrain", "GameData/Terrain/A001.bin.lz", compressed=True)
    multi_test("terrain", "GameData/Terrain/A005.bin.lz", compressed=True)
    multi_test("dispos", "GameData/Dispos/A003.bin.lz", compressed=True)
    multi_test("dispos", "GameData/Dispos/A004.bin.lz", compressed=True)
    multi_test(
        "field_config", "GameData/Field/Btl_AnotherDimension.bin", compressed=False
    )
    multi_test(
        "field_config", "GameData/Field/Btl_CapitalDark_CityArea.bin", compressed=False
    )
    multi_test("field_config", "GameData/Field/Btl_PortDia.bin", compressed=False)
    fates_new_chapter_test()


def test_fe15():
    basic_test("characters", "Data/Person.bin.lz")
    basic_test("skills", "Data/Skill.bin.lz")
    basic_test("belongs", "Data/Belong.bin.lz")
    basic_test("amiibos", "Data/Amiibo.bin.lz")
    basic_test("call_tables", "Data/CallTable.bin.lz")
    basic_test("terrain", "Data/Terrain.bin.lz")
    basic_test("side_stories", "Data/SideStory.bin.lz")
    basic_test("plants", "Data/Plant.bin.lz")
    basic_test("jobs", "Data/Job.bin.lz")
    basic_test("items", "Data/Item.bin.lz")
    basic_test("reliance", "Data/Reliance.bin.lz")
    basic_test("portraits", "face/FaceData.bin.lz")
    basic_test("dungeon", "Data/Dungeon.bin.lz")
    basic_test("field", "Data/Field.bin.lz")
    basic_test("access", "Data/Access.bin.lz")
    basic_test("epilogue", "Data/Epilogue.bin.lz")
    basic_test("hub_talk", "Data/HubTalk.bin.lz")
    basic_test("effect", "Data/Effect.bin.lz")
    basic_test("rom0", "asset/ROM0.lz")
    basic_test("rom1", "asset/ROM1.lz")
    basic_test("rom2", "asset/ROM2.lz")
    basic_test("rom3", "asset/ROM3.lz")
    basic_test("rom4", "asset/ROM4.lz")
    basic_test("rom5", "asset/ROM5.lz")
    basic_test("rom6", "asset/ROM6.lz")
    basic_test("chapters", "Data/Chapter.bin.lz")
    multi_test("grids", "Data/Terrain/ソフィアの北.bin.lz")
    multi_test("dispos", "Data/Dispos/ラムの林.bin.lz")
    multi_test("dispos", "Data/Dispos/ソフィアの北.bin.lz")
    multi_test("events", "Data/Event/ソフィア城.bin.lz")
    multi_test("events", "Data/Event/ドーマ神殿.bin.lz")
    multi_test("events", "Data/Event/ソフィアの港.bin.lz")
    multi_test("events", "Data/Event/ソフィアの北.bin.lz")
    multi_test("events", "Data/Event/ラムの村.bin.lz")
    multi_test("field_references", "field/dng_amiibo_CELLICA_1.bin.lz")
    multi_test("field_files", "field/dng_amiibo_CELLICA_1.bin.lz")
    fe15_event_compile_test()


if __name__ == "__main__":
    if not os.path.exists("Data"):
        print(
            "Error: This script must be executed from the root of the paragon repository."
        )
        exit(1)
    if len(sys.argv) < 4:
        print(
            "Format: python module_test.py <FE10|FE13|FE14|FE15> <Language> <Extracted RomFS Path>"
        )
        exit(1)
    game = sys.argv[1]
    language = sys.argv[2]
    rom_root = sys.argv[3]
    config_root = os.path.abspath(os.path.join("Data", game))

    print(f"Using config root: {config_root}")
    output_root = tempfile.mkdtemp()
    print(f"Outputting to tempdir: {output_root}")
    try:
        for i in range(0, 3):
            print(f"Running tests round {i+1}")
            print("Loading game data...")
            gd = pgn.GameData.load(output_root, rom_root, game, language, config_root)
            print("Reading game data...")
            gd.read()
            print("Done - beginning tests.")
            print()
            if game == "FE10":
                test_fe10()
            elif game == "FE13":
                test_fe13()
            elif game == "FE14":
                test_fe14()
            else:
                test_fe15()
            print()
    finally:
        shutil.rmtree(output_root)
