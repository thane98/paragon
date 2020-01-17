from model.fe14.dispo import Dispo
from model.fe14.terrain import Terrain
from services.service_locator import locator


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


class ChapterData:
    def __init__(self, chapter):
        self.chapter = chapter
        self.config = _open_map_config(chapter)
        self.dispos = _open_dispos(chapter)
        self.terrain = _open_terrain(chapter)
        self.person = _open_person(chapter)
