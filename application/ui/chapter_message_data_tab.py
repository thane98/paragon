from model.fe14.chapter_data import ChapterData
from ui.fe14.fe14_conversation_editor import FE14ConversationEditor


class ChapterMessageDataTab(FE14ConversationEditor):
    def update_chapter_data(self, chapter_data: ChapterData):
        if chapter_data:
            self.set_archive(chapter_data.conversation_data)
        else:
            self.set_archive(None)
