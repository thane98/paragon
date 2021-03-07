from paragon.ui.controllers.avatar_config_window import AvatarConfigWindow


class FE13AvatarConfigWindow(AvatarConfigWindow):
    def __init__(self, ms, gs):
        super().__init__(ms, gs, ms.config.fe13_avatar)

    def _portrait_options(self):
        return [
            ("Male 1", "FID_プレイヤー"),
            ("Male 2A", "FID_マイユニ_童顔_顔立ちA"),
            ("Male 2B", "FID_マイユニ_童顔_顔立ちB"),
            ("Male 2C", "FID_マイユニ_童顔_顔立ちC"),
            ("Male 2D", "FID_マイユニ_童顔_顔立ちD"),
            ("Male 2E", "FID_マイユニ_童顔_顔立ちE"),
            ("Male 3A", "FID_マイユニ_青年_顔立ちA"),
            ("Male 3B", "FID_マイユニ_青年_顔立ちB"),
            ("Male 3C", "FID_マイユニ_青年_顔立ちC"),
            ("Male 3D", "FID_マイユニ_青年_顔立ちD"),
            ("Male 3E", "FID_マイユニ_青年_顔立ちE"),
            ("Male 4A", "FID_マイユニ_ゴツイ_顔立ちA"),
            ("Male 4B", "FID_マイユニ_ゴツイ_顔立ちB"),
            ("Male 4C", "FID_マイユニ_ゴツイ_顔立ちC"),
            ("Male 4D", "FID_マイユニ_ゴツイ_顔立ちD"),
            ("Male 4E", "FID_マイユニ_ゴツイ_顔立ちE"),
            ("Female 1A", "FID_マイユニ_ロリ_顔立ちA"),
            ("Female 1B", "FID_マイユニ_ロリ_顔立ちB"),
            ("Female 1C", "FID_マイユニ_ロリ_顔立ちC"),
            ("Female 1D", "FID_マイユニ_ロリ_顔立ちD"),
            ("Female 1E", "FID_マイユニ_ロリ_顔立ちE"),
            ("Female 2A", "FID_マイユニ_少女_顔立ちA"),
            ("Female 2B", "FID_マイユニ_少女_顔立ちB"),
            ("Female 2C", "FID_マイユニ_少女_顔立ちC"),
            ("Female 2D", "FID_マイユニ_少女_顔立ちD"),
            ("Female 2E", "FID_マイユニ_少女_顔立ちE"),
            ("Female 3A", "FID_マイユニ_妙齢_顔立ちA"),
            ("Female 3B", "FID_マイユニ_妙齢_顔立ちB"),
            ("Female 3C", "FID_マイユニ_妙齢_顔立ちC"),
            ("Female 3D", "FID_マイユニ_妙齢_顔立ちD"),
            ("Female 3E", "FID_マイユニ_妙齢_顔立ちE"),
        ]

    def _accessory_options(self):
        return []

    def _supports_accessories(self):
        return False

    def _portrait_mode(self):
        return "BU"
