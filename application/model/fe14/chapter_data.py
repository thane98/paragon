from model.fe14.dispo import Dispo
from model.fe14.terrain import Terrain
from services.service_locator import locator
from utils.chapter_utils import detect_route_from_dispo_location, search_all_routes_for_file, \
    detect_chapter_file_sub_folder


def _open_map_config(chapter):
    truncated_cid = chapter["CID"].value[4:]
    target_path = "/map/config/%s.bin" % truncated_cid
    open_files_service = locator.get_scoped("OpenFilesService")
    if not open_files_service.exists(target_path):
        return None
    module_service = locator.get_scoped("ModuleService")
    common_module_service = locator.get_scoped("CommonModuleService")
    module_template = module_service.get_common_module_template("Map Config")
    module = common_module_service.open_common_module(module_template, target_path)
    return module


def _open_dispos(chapter):
    target_file = "%s.bin.lz" % chapter["CID"].value[4:]
    target_path = search_all_routes_for_file("/GameData/Dispos/", target_file)
    if not target_path:
        return None
    open_files_service = locator.get_scoped("OpenFilesService")
    archive = open_files_service.open(target_path)
    dispos = Dispo()
    dispos.read(archive)
    return dispos


def _open_terrain(chapter):
    target_file = "%s.bin.lz" % chapter["CID"].value[4:]
    target_path = search_all_routes_for_file("/GameData/Terrain/", target_file)
    if not target_path:
        return None
    open_files_service = locator.get_scoped("OpenFilesService")
    archive = open_files_service.open(target_path)
    terrain = Terrain()
    terrain.read(archive)
    return terrain


def _open_person(chapter):
    target_file = "%s.bin.lz" % chapter["CID"].value[4:]
    target_path = search_all_routes_for_file("/GameData/Person/", target_file)
    if not target_path:
        return None
    module_service = locator.get_scoped("ModuleService")
    common_module_service = locator.get_scoped("CommonModuleService")
    module_template = module_service.get_common_module_template("Person")
    module = common_module_service.open_common_module(module_template, target_path)
    return module


class ChapterData:
    def __init__(self, chapter):
        self.chapter = chapter
        self.file_location = detect_route_from_dispo_location(chapter)
        self.config = _open_map_config(chapter)
        self.dispos = _open_dispos(chapter)
        self.terrain = _open_terrain(chapter)
        self.person = _open_person(chapter)

    def save(self):
        if self.dispos and self.terrain:
            target_file = "%s.bin.lz" % self.chapter["CID"].value[4:]
            suffix = detect_chapter_file_sub_folder(self.chapter) + target_file
            dispos_path = "/GameData/Dispos/" + suffix
            terrain_path = "/GameData/Terrain/" + target_file
            dispos_archive = self.dispos.to_bin()
            terrain_archive = self.terrain.to_bin()
            open_files_service = locator.get_scoped("OpenFilesService")
            open_files_service.register_or_overwrite_archive(dispos_path, dispos_archive)
            open_files_service.register_or_overwrite_archive(terrain_path, terrain_archive)
