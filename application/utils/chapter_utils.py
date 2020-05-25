from enum import Enum

from services.service_locator import locator


class ChapterFileLocation(Enum):
    ALL_ROUTES = 0
    BIRTHRIGHT = 1
    CONQUEST = 2
    REVELATION = 3
    NO_ROUTE = 4


_SUFFIXES = {
    ChapterFileLocation.ALL_ROUTES: "",
    ChapterFileLocation.BIRTHRIGHT: "/A/",
    ChapterFileLocation.CONQUEST: "/B/",
    ChapterFileLocation.REVELATION: "/C/",
    ChapterFileLocation.NO_ROUTE: None
}


def search_all_routes_for_file(base_path, file):
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
        return None


def search_all_routes_for_file_localized(base_path, file):
    open_files_service = locator.get_scoped("OpenFilesService")
    if open_files_service.localized_exists(base_path + file):
        return base_path + file
    elif open_files_service.localized_exists(base_path + "/A/" + file):
        return base_path + "/A/" + file
    elif open_files_service.localized_exists(base_path + "/B/" + file):
        return base_path + "/B/" + file
    elif open_files_service.localized_exists(base_path + "/C/" + file):
        return base_path + "/C/" + file
    else:
        return None


def detect_route_from_dispo_location(chapter):
    target_file = "%s.bin.lz" % chapter["CID"].value[4:]
    target_path = search_all_routes_for_file("/GameData/Dispos/", target_file)
    if not target_path:
        return ChapterFileLocation.NO_ROUTE
    if target_path.endswith("/A/" + target_file):
        return ChapterFileLocation.BIRTHRIGHT
    elif target_path.endswith("/B/" + target_file):
        return ChapterFileLocation.CONQUEST
    elif target_path.endswith("/C/" + target_file):
        return ChapterFileLocation.REVELATION
    return ChapterFileLocation.ALL_ROUTES


def detect_chapter_file_sub_folder(chapter):
    route = detect_route_from_dispo_location(chapter)
    return _SUFFIXES[route]
