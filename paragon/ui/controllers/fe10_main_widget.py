from paragon.ui.views.ui_fe10_main_widget import Ui_FE10MainWidget


class FE10MainWidget(Ui_FE10MainWidget):
    def __init__(self, ms, gs, main_window):
        super().__init__()
        self.gs = gs
        self.ms = ms
        self.main_window = main_window

        self.chapters_button.clicked.connect(lambda: self.main_window.open_node_by_id("chapters"))
        self.characters_button.clicked.connect(lambda: self.main_window.open_node_by_id("characters"))
        self.classes_button.clicked.connect(lambda: self.main_window.open_node_by_id("jobs"))
        self.items_button.clicked.connect(lambda: self.main_window.open_node_by_id("items"))
        self.skills_button.clicked.connect(lambda: self.main_window.open_node_by_id("skills"))
        self.armies_button.clicked.connect(lambda: self.main_window.open_node_by_id("groups"))
        self.tiles_button.clicked.connect(lambda: self.main_window.open_node_by_id("tiles"))
        self.supports_button.clicked.connect(lambda: self.main_window.open_node_by_id("main_support_table"))
        self.no_battle_button.clicked.connect(lambda: self.main_window.open_node_by_id("no_battle"))
        self.portraits_button.clicked.connect(lambda: self.main_window.open_node_by_id("facedata"))

    def on_close(self):
        pass
