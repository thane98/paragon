import os
import shutil
import sys
import tempfile
import traceback

from paragon.model.fe14_chapter_route import FE14ChapterRoute

from paragon.core.services.fe13_chapters import FE13Chapters

from paragon import paragon as pgn
from paragon.core.services.fe14_chapters import FE14Chapters


def accuracy_test(rom_root, output_root, path_in_rom, path_in_output, compressed):
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


def basic_test(gd, rom_root, output_root, store_id, path_in_rom, compressed=True):
    print(f"Testing accuracy for '{store_id}' with output path '{path_in_rom}'... ", end='')
    try:
        gd.set_store_dirty(store_id, True)
        gd.write()
        accuracy_test(rom_root, output_root, path_in_rom, path_in_rom, compressed)
    except:
        print("FAILURE! Encountered exception:")
        traceback.print_exc()
    gd.set_store_dirty(store_id, False)


def multi_test(gd, rom_root, output_root, multi_id, path_in_rom, compressed=True):
    print(f"Testing accuracy for multi '{multi_id}' with output path '{path_in_rom}'... ", end='')
    try:
        gd.multi_open(multi_id, path_in_rom)
        gd.multi_set_dirty(multi_id, path_in_rom, True)
        gd.write()
        accuracy_test(rom_root, output_root, path_in_rom, path_in_rom, compressed)
    except:
        print("FAILURE! Encountered exception:")
        traceback.print_exc()
    gd.multi_set_dirty(multi_id, path_in_rom, False)


def awakening_new_chapter_test(gd, rom_root, output_root):
    print(f"Testing accuracy for creating a new chapter...")
    try:
        chapters = FE13Chapters(gd, None, None)
        data = chapters.new("CID_X001", "CID_TEST")
        chapters.set_dirty(data, True)
        gd.write()
        print("\tDispos...", end='')
        accuracy_test(
            rom_root,
            output_root,
            "data/dispos/X001.bin.lz",
            "data/dispos/TEST.bin.lz",
            True
        )
        print("\tPerson...", end='')
        accuracy_test(
            rom_root,
            output_root,
            "data/person/X001.bin.lz",
            "data/person/TEST.bin.lz",
            True
        )
        print("\tGrids...", end='')
        accuracy_test(
            rom_root,
            output_root,
            "data/terrain/X001.bin.lz",
            "data/terrain/TEST.bin.lz",
            True
        )
        print("\tLandscape...", end='')
        accuracy_test(
            rom_root,
            output_root,
            "data/landscape/X001.bin.lz",
            "data/landscape/TEST.bin.lz",
            True
        )
        print("\tMap Config...", end='')
        accuracy_test(
            rom_root,
            output_root,
            "map/data/X001.bin",
            "map/data/TEST.bin",
            False
        )
        chapters.set_dirty(data, False)
    except:
        print("FAILURE! Encountered exception:")
        traceback.print_exc()


def awakening_gamedata_test(gd, rom_root, output_root):
    print("Testing accuracy for GameData ignoring ItemDataNum address... ", end='')
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


def fates_gamedata_test(gd, rom_root, output_root):
    print("Testing accuracy for GameData by comparing regions...", end='')
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
            ]
        )
        print("Success.")
    except:
        print("FAILURE! Encountered exception:")
        traceback.print_exc()
    gd.set_store_dirty("gamedata", False)


def fates_new_chapter_test(gd, rom_root, output_root):
    print(f"Testing accuracy for creating a new chapter...")
    try:
        chapters = FE14Chapters(gd, None, None)
        data = chapters.new("CID_B015", "CID_TEST", route=FE14ChapterRoute.BIRTHRIGHT)
        chapters.set_dirty(data, True)
        gd.write()
        print("\tDispos...", end='')
        accuracy_test(
            rom_root,
            output_root,
            "GameData/Dispos/B/B015.bin.lz",
            "GameData/Dispos/A/TEST.bin.lz",
            True
        )
        print("\tTerrain...", end='')
        accuracy_test(
            rom_root,
            output_root,
            "GameData/Terrain/B015.bin.lz",
            "GameData/Terrain/TEST.bin.lz",
            True
        )
        print("\tMap Config...", end='')
        accuracy_test(
            rom_root,
            output_root,
            "map/config/B015.bin",
            "map/config/TEST.bin",
            False
        )
        chapters.set_dirty(data, False)
    except:
        print("FAILURE! Encountered exception:")
        traceback.print_exc()


def test_fe13(gd, rom_root, output_root):
    awakening_gamedata_test(gd, rom_root, output_root)
    basic_test(
        gd,
        rom_root,
        output_root,
        "portraits",
        "face/FaceData.bin.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "characters",
        "data/person/static.bin.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "combotbl",
        "bs/ComboTbl.bin.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "combotbl_presets",
        "bs/Presets.bin.lz"
    )
    multi_test(
        gd,
        rom_root,
        output_root,
        "grids",
        "data/terrain/000.bin.lz"
    )
    multi_test(
        gd,
        rom_root,
        output_root,
        "grids",
        "data/terrain/X005.bin.lz"
    )
    multi_test(
        gd,
        rom_root,
        output_root,
        "dispos",
        "data/dispos/000.bin.lz"
    )
    multi_test(
        gd,
        rom_root,
        output_root,
        "dispos",
        "data/dispos/X003.bin.lz"
    )
    multi_test(
        gd,
        rom_root,
        output_root,
        "map_configs",
        "map/data/000.bin",
        compressed=False
    )
    multi_test(
        gd,
        rom_root,
        output_root,
        "map_configs",
        "map/data/007.bin",
        compressed=False
    )
    multi_test(
        gd,
        rom_root,
        output_root,
        "landscape",
        f"data/landscape/023.bin.lz",
        compressed=True
    )
    multi_test(
        gd,
        rom_root,
        output_root,
        "landscape",
        f"data/landscape/X021.bin.lz",
        compressed=True
    )
    if language == "EnglishNA":
        basic_test(
            gd,
            rom_root,
            output_root,
            "indirect_sound_english",
            "sound/IndirectSound_US_EN.bin.lz"
        )
        basic_test(
            gd,
            rom_root,
            output_root,
            "indirect_sound_japanese_us",
            "sound/IndirectSound_US_JP.bin.lz"
        )
    awakening_new_chapter_test(gd, rom_root, output_root)


def test_fe14(gd, rom_root, output_root):
    fates_gamedata_test(gd, rom_root, output_root)
    basic_test(
        gd,
        rom_root,
        output_root,
        "castle_join",
        "castle/castle_join.bin.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "castle_building",
        "castle/castle_building.bin.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "game_effect",
        "GameData/GameEffect.bin.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "accessories",
        "GameData/AcceShop.bin.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "facedata",
        "face/FaceData.bin.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "rom0",
        "asset/ROM0.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "rom1",
        "asset/ROM1.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "rom2",
        "asset/ROM2.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "rom3",
        "asset/ROM3.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "rom4",
        "asset/ROM4.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "rom5",
        "asset/ROM5.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "rom6",
        "asset/ROM6.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "camera_data",
        "GameData/CameraData.bin.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "butler",
        "GameData/Castle/Butler.bin.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "geoattr",
        "GameData/GeoAttr.bin.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "reliance_bgm",
        "talk/RelianceTalkBGM.bin",
        compressed=False
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "texture_coordinate",
        "TextureCoordinate.bin",
        compressed=False
    )
    multi_test(
        gd,
        rom_root,
        output_root,
        "map_configs",
        f"map/config/A000.bin",
        compressed=False
    )
    multi_test(
        gd,
        rom_root,
        output_root,
        "map_configs",
        f"map/config/B028.bin",
        compressed=False
    )
    multi_test(
        gd,
        rom_root,
        output_root,
        "terrain",
        f"GameData/Terrain/A001.bin.lz",
        compressed=True
    )
    multi_test(
        gd,
        rom_root,
        output_root,
        "terrain",
        f"GameData/Terrain/A005.bin.lz",
        compressed=True
    )
    multi_test(
        gd,
        rom_root,
        output_root,
        "dispos",
        f"GameData/Dispos/A003.bin.lz",
        compressed=True
    )
    multi_test(
        gd,
        rom_root,
        output_root,
        "dispos",
        f"GameData/Dispos/A004.bin.lz",
        compressed=True
    )
    fates_new_chapter_test(gd, rom_root, output_root)


def test_fe15(gd, rom_root, output_root):
    basic_test(
        gd,
        rom_root,
        output_root,
        "characters",
        "Data/Person.bin.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "skills",
        "Data/Skill.bin.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "belongs",
        "Data/Belong.bin.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "amiibos",
        "Data/Amiibo.bin.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "call_tables",
        "Data/CallTable.bin.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "terrain",
        "Data/Terrain.bin.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "side_stories",
        "Data/SideStory.bin.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "plants",
        "Data/Plant.bin.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "jobs",
        "Data/Job.bin.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "items",
        "Data/Item.bin.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "reliance",
        "Data/Reliance.bin.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "portraits",
        "face/FaceData.bin.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "rom0",
        "asset/ROM0.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "rom1",
        "asset/ROM1.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "rom2",
        "asset/ROM2.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "rom3",
        "asset/ROM3.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "rom4",
        "asset/ROM4.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "rom5",
        "asset/ROM5.lz"
    )
    basic_test(
        gd,
        rom_root,
        output_root,
        "rom6",
        "asset/ROM6.lz"
    )


if __name__ == "__main__":
    if not os.path.exists("Data"):
        print("Error: This script must be executed from the root of the paragon repository.")
        exit(1)
    if len(sys.argv) < 4:
        print("Format: python module_test.py <FE13|FE14|FE15> <Language> <Extracted RomFS Path>")
        exit(1)
    game = sys.argv[1]
    language = sys.argv[2]
    path = sys.argv[3]
    config_root = os.path.abspath(os.path.join("Data", game))

    print(f"Using config root: {config_root}")
    tmp = tempfile.mkdtemp()
    print(f"Outputting to temp. dir: {tmp}")
    try:
        print("Loading game data...")
        gd = pgn.GameData.load(
            tmp,
            path,
            game,
            language,
            config_root
        )
        print("Reading game data...")
        gd.read()
        print("Done - beginning tests.")
        print()
        if game == "FE13":
            test_fe13(gd, path, tmp)
        elif game == "FE14":
            test_fe14(gd, path, tmp)
        else:
            test_fe15(gd, path, tmp)
        print()
    finally:
        shutil.rmtree(tmp)
