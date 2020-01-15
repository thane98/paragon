from services.service_locator import locator


def _open_map_config(chapter):
    truncated_cid = chapter["CID"].value[4:]
    target_path = "/map/config/%s.bin" % truncated_cid
    driver = locator.get_scoped("Driver")
    base_module = driver.common_modules["Map Config"]
    module = driver.handle_open_for_common_module(base_module, target_path)
    return module


class ChapterData:
    def __init__(self, chapter):
        self.chapter = chapter
        self.config = _open_map_config(chapter)
