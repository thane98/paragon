import os
import shutil
import sys
import tempfile
import traceback

from paragon import paragon as pgn


def basic_test(gd, rom_root, output_root, store_id, path_in_rom, compressed=True):
    print(f"Testing accuracy for '{store_id}' with output path '{path_in_rom}'... ", end='')
    try:
        gd.mark_store_dirty(store_id)
        gd.write()
        original_path = os.path.join(rom_root, path_in_rom)
        new_path = os.path.join(output_root, path_in_rom)
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
    except:
        print("FAILURE! Encountered exception:")
        traceback.print_exc()


def awakening_gamedata_test(gd, rom_root, output_root):
    print("Testing accuracy for GameData ignoring ItemDataNum address... ", end='')
    try:
        gd.mark_store_dirty("gamedata")
        gd.write()
        original_path = os.path.join(rom_root, "data/GameData.bin.lz")
        new_path = os.path.join(output_root, "data/GameData.bin.lz")
        with open(original_path, "rb") as f:
            original = f.read()
        with open(new_path, "rb") as f:
            new = f.read()
        original = pgn.load_awakening_gamedata_for_tests(original_path)
        new = pgn.load_awakening_gamedata_for_tests(new_path)
        if original != new:
            print("FAILURE! Files do not match.")
        else:
            print("Success.")
    except:
        print("FAILURE! Encountered exception:")
        traceback.print_exc()


def test_fe13(gd, rom_root, output_root):
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
    awakening_gamedata_test(gd, rom_root, output_root)


def test_fe14(gd):
    print("No tests available.")


def test_fe15(gd):
    print("No tests available.")


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
            test_fe14(gd)
        else:
            test_fe15(gd)
        print()
    finally:
        shutil.rmtree(tmp)
