from paragon.ui.controllers.avatar_config_window import AvatarConfigWindow


_PORTRAIT_OPTIONS = [
    ("Male 1A", "FID_マイユニ_男1_顔A"),
    ("Male 1B", "FID_マイユニ_男1_顔B"),
    ("Male 1C", "FID_マイユニ_男1_顔C"),
    ("Male 1D", "FID_マイユニ_男1_顔D"),
    ("Male 1E", "FID_マイユニ_男1_顔E"),
    ("Male 1F", "FID_マイユニ_男1_顔F"),
    ("Male 1G", "FID_マイユニ_男1_顔G"),
    ("Male 1H", "FID_マイユニ_男1_顔H"),
    ("Male 1I", "FID_マイユニ_男1_顔I"),
    ("Male 1J", "FID_マイユニ_男1_顔J"),
    ("Male 2A", "FID_マイユニ_男2_顔A"),
    ("Male 2B", "FID_マイユニ_男2_顔B"),
    ("Male 2C", "FID_マイユニ_男2_顔C"),
    ("Male 2D", "FID_マイユニ_男2_顔D"),
    ("Male 2E", "FID_マイユニ_男2_顔E"),
    ("Male 2F", "FID_マイユニ_男2_顔F"),
    ("Male 2G", "FID_マイユニ_男2_顔G"),
    ("Male 2H", "FID_マイユニ_男2_顔H"),
    ("Male 2I", "FID_マイユニ_男2_顔I"),
    ("Male 2J", "FID_マイユニ_男2_顔J"),
    ("Female 1A", "FID_マイユニ_女1_顔A"),
    ("Female 1B", "FID_マイユニ_女1_顔B"),
    ("Female 1C", "FID_マイユニ_女1_顔C"),
    ("Female 1D", "FID_マイユニ_女1_顔D"),
    ("Female 1E", "FID_マイユニ_女1_顔E"),
    ("Female 1F", "FID_マイユニ_女1_顔F"),
    ("Female 1G", "FID_マイユニ_女1_顔G"),
    ("Female 1H", "FID_マイユニ_女1_顔H"),
    ("Female 1I", "FID_マイユニ_女1_顔I"),
    ("Female 1J", "FID_マイユニ_女1_顔J"),
    ("Female 2A", "FID_マイユニ_女2_顔A"),
    ("Female 2B", "FID_マイユニ_女2_顔B"),
    ("Female 2C", "FID_マイユニ_女2_顔C"),
    ("Female 2D", "FID_マイユニ_女2_顔D"),
    ("Female 2E", "FID_マイユニ_女2_顔E"),
    ("Female 2F", "FID_マイユニ_女2_顔F"),
    ("Female 2G", "FID_マイユニ_女2_顔G"),
    ("Female 2H", "FID_マイユニ_女2_顔H"),
    ("Female 2I", "FID_マイユニ_女2_顔I"),
    ("Female 2J", "FID_マイユニ_女2_顔J")
]


_ACCESSORY_OPTIONS = [
    ("None", None),
    ("1", "アクセサリ1_1"),
    ("2", "アクセサリ1_2"),
    ("3", "アクセサリ1_3"),
    ("4", "アクセサリ1_4"),
    ("5", "アクセサリ1_5"),
    ("6", "アクセサリ1_6"),
    ("7", "アクセサリ1_7"),
    ("8", "アクセサリ1_8"),
    ("9", "アクセサリ1_9"),
    ("10", "アクセサリ1_10"),
    ("11", "アクセサリ1_11")
]


class FE14AvatarConfigWindow(AvatarConfigWindow):
    def __init__(self, ms, gs):
        super().__init__(ms, gs, ms.config.fe14_avatar)

    def _portrait_options(self):
        return _PORTRAIT_OPTIONS

    def _accessory_options(self):
        return _ACCESSORY_OPTIONS

    def _supports_accessories(self):
        return True

    def _portrait_mode(self):
        return "ST"
