from paragon.model.project import Project
from paragon.model.game import Game
from typing import List

import os


def sanity_check_files(project: Project) -> bool:
    """
    Perform sanity checks for the project.
    This determines if the project's ROM/output paths make sense.
    Returns a list of issues or empty list if there are no problems.
    """
    if project.game == Game.FE9:
        files_to_check = ["system.cmp"]
    elif project.game == Game.FE10:
        files_to_check = ["FE10Data.cms", "Face/facedata.bin"]
    elif project.game == Game.FE13:
        files_to_check = [
            "data/person/static.bin.lz",
            "face/FaceData.bin.lz",
            "bs/ComboTbl.bin.lz",
        ]
    elif project.game == Game.FE14:
        files_to_check = ["bs/aset.lz", "asset/ROM3.lz", "GameData/GameData.bin.lz"]
    else:
        files_to_check = ["Data/Person.bin.lz", "face/FaceData.bin.lz"]
    for f in files_to_check:
        path = os.path.join(project.rom_path, f)
        if not os.path.isfile(path):
            return False
    return True


def sanity_check_romfs_bin(project: Project) -> bool:
    """
    This checks for a common pattern where the user selects a directory
    containing romfs.bin instead of an extracted RomFS
    """
    return not os.path.isfile(os.path.join(project.rom_path, "romfs.bin"))
