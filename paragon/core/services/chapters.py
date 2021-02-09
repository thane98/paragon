from paragon.model.chapter_data import ChapterData


class Chapters:
    def __init__(self, gd):
        self.gd = gd
        self.chapters = {}

    def validate_cid_for_new_chapter(self, cid):
        if not cid.startswith("CID_"):
            raise ValueError("Chapter CID must start with 'CID_'")
        if self.cid_in_use(cid):
            raise ValueError(
                f"CID '{cid}' is already used by a different chapter. Please enter a unique CID."
            )

    def cid_in_use(self, cid: str) -> bool:
        rid, field_id = self.gd.table("chapters")
        for chapter in self.gd.items(rid, field_id):
            if self.gd.key(chapter) == cid:
                return True
        return False

    def load(self, cid: str) -> ChapterData:
        if cid in self.chapters:
            return self.chapters[cid]
        else:
            data = self._load(cid)
            self.chapters[cid] = data
            return data

    def new(self, source: str, dest: str, **kwargs) -> ChapterData:
        # Verify that the dest CID is not overwriting something.
        if self.cid_in_use(dest):
            raise KeyError(f"Cannot overwrite {dest} with a new chapter.")
        data = self._new(source, dest)
        self.set_dirty(data, True)
        self.chapters[dest] = data
        return data

    def _new(self, source: str, dest: str, **kwargs) -> ChapterData:
        raise NotImplementedError

    def set_dirty(self, chapter_data: ChapterData, dirty: bool):
        raise NotImplementedError

    def _load(self, cid: str) -> ChapterData:
        raise NotImplementedError
