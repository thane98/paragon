from model.fe14.chapter_data import ChapterData
from ui.fe14_chapter_editor import FE14ChapterEditor


class ChapterService:
    def __init__(self):
        self.editor = FE14ChapterEditor()
        self.open_chapters = {}

    def get_chapter_data_from_chapter(self, chapter):
        cid = chapter["CID"].value
        if cid in self.open_chapters:
            return self.open_chapters[cid]
        chapter_data = ChapterData(chapter)
        self.open_chapters[cid] = chapter_data
        return chapter_data

    def get_display_name(self):
        return "Chapters"

    def save(self):
        for chapter_data in self.open_chapters.values():
            chapter_data.save()
