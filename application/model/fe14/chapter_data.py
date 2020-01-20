from enum import Enum

from model.fe14.dispo import Dispo
from model.fe14.terrain import Terrain
from services.service_locator import locator


class ChapterFileLocation(Enum):
    ALL_ROUTES = 0
    BIRTHRIGHT = 1
    CONQUEST = 2
    REVELATION = 3


_SUFFIXES = {
    ChapterFileLocation.ALL_ROUTES: "",
    ChapterFileLocation.BIRTHRIGHT: "/A/",
    ChapterFileLocation.CONQUEST: "/B/",
    ChapterFileLocation.REVELATION: "/C/"
}


def _search_all_routes_for_file(base_path, file):
    open_files_service = locator.get_scoped("OpenFilesService")
    if open_files_service.exists(base_path + file):
        return base_path + file
    elif open_files_service.exists(base_path + "/A/" + file):
        return base_path + "/A/" + file
    elif open_files_service.exists(base_path + "/B/" + file):
        return base_path + "/B/" + file
    elif open_files_service.exists(base_path + "/C/" + file):
        return base_path + "/C/" + file
    else:
        raise Exception


def _open_map_config(chapter):
    truncated_cid = chapter["CID"].value[4:]
    target_path = "/map/config/%s.bin" % truncated_cid
    driver = locator.get_scoped("Driver")
    base_module = driver.common_modules["Map Config"]
    module = driver.handle_open_for_common_module(base_module, target_path)
    return module


def _open_dispos(chapter):
    target_file = "%s.bin.lz" % chapter["CID"].value[4:]
    target_path = _search_all_routes_for_file("/GameData/Dispos/", target_file)
    open_files_service = locator.get_scoped("OpenFilesService")
    archive = open_files_service.open(target_path)
    dispos = Dispo()
    dispos.read(archive)
    return dispos


def _open_terrain(chapter):
    target_file = "%s.bin.lz" % chapter["CID"].value[4:]
    target_path = _search_all_routes_for_file("/GameData/Terrain/", target_file)
    open_files_service = locator.get_scoped("OpenFilesService")
    archive = open_files_service.open(target_path)
    terrain = Terrain()
    terrain.read(archive)
    return terrain


def _open_person(chapter):
    target_file = "%s.bin.lz" % chapter["CID"].value[4:]
    target_path = _search_all_routes_for_file("/GameData/Person/", target_file)
    driver = locator.get_scoped("Driver")
    base_module = driver.common_modules["Person"]
    module = driver.handle_open_for_common_module(base_module, target_path)
    return module


def _detect_route_from_dispo_location(chapter):
    target_file = "%s.bin.lz" % chapter["CID"].value[4:]
    target_path = _search_all_routes_for_file("/GameData/Dispos/", target_file)
    if target_path.endswith("/A/" + target_file):
        return ChapterFileLocation.BIRTHRIGHT
    elif target_path.endswith("/B/" + target_file):
        return ChapterFileLocation.CONQUEST
    elif target_path.endswith("/C/" + target_file):
        return ChapterFileLocation.REVELATION
    return ChapterFileLocation.ALL_ROUTES


class ChapterData:
    def __init__(self, chapter):
        self.chapter = chapter
        self.file_location = _detect_route_from_dispo_location(chapter)
        self.config = _open_map_config(chapter)
        self.dispos = _open_dispos(chapter)
        self.terrain = _open_terrain(chapter)
        self.person = _open_person(chapter)

    def save(self):
        target_file = "%s.bin.lz" % self.chapter["CID"].value[4:]
        suffix = _SUFFIXES[self.file_location] + target_file
        dispos_path = "/GameData/Dispos/" + suffix
        terrain_path = "/GameData/Terrain/" + suffix
        dispos_archive = self.dispos.to_bin()
        terrain_archive = self.terrain.to_bin()

        open_files_service = locator.get_scoped("OpenFilesService")
        open_files_service.register_or_overwrite_archive(dispos_path, dispos_archive)
        open_files_service.register_or_overwrite_archive(terrain_path, terrain_archive)
