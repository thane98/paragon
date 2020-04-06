from services.service_locator import locator
from ui.simple_editor import SimpleEditor


class FE14ChapterCharactersTab(SimpleEditor):
    def __init__(self):
        module_service = locator.get_scoped("ModuleService")
        SimpleEditor.__init__(self, module_service.get_common_module_template("Person"))

    def update_chapter_data(self, chapter_data):
        if chapter_data.person:
            self.setEnabled(True)
            self.add_button.setEnabled(True)
            self.module = chapter_data.person
            self.model = self.module.entries_model
            self.proxy_model.setSourceModel(self.model)
        else:
            self.setEnabled(False)
            self.add_button.setEnabled(False)
        self.property_form.update_target(None)
