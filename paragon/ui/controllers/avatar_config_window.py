from PySide6 import QtCore

from paragon.ui.views.ui_avatar_config_window import Ui_AvatarConfigWindow


class AvatarConfigWindow(Ui_AvatarConfigWindow):
    def __init__(self, ms, gs, config):
        super().__init__(ms, gs)

        self.config = config
        self.gd = gs.data
        self.service = gs.portraits

        for name, fsid in self._portrait_options():
            self.portraits.addItem(name, fsid)
        for name, accessory in self._accessory_options():
            self.accessory.addItem(name, accessory)
        if not self._supports_accessories():
            self.accessory.setEnabled(False)

        self._set_fields_from_config()

        self.name.textChanged.connect(self._on_name_changed)
        self.gender.currentIndexChanged.connect(self._on_gender_changed)
        self.portraits.currentIndexChanged.connect(self._on_portraits_changed)
        self.accessory.currentIndexChanged.connect(self._on_accessory_changed)

    def _set_fields_from_config(self):
        self.name.setText(self.config.name)
        self.portraits.setCurrentIndex(-1)
        self.gender.setCurrentIndex(-1)
        self.accessory.setCurrentIndex(-1)
        for i in range(0, self.gender.count()):
            if self.gender.itemData(i, QtCore.Qt.DisplayRole) == self.config.gender:
                self.gender.setCurrentIndex(i)
                break
        for i in range(0, self.portraits.count()):
            if self.portraits.itemData(i, QtCore.Qt.UserRole) == self.config.portraits:
                self.portraits.setCurrentIndex(i)
                break
        if self._supports_accessories():
            for i in range(0, self.accessory.count()):
                if (
                    self.accessory.itemData(i, QtCore.Qt.UserRole)
                    == self.config.accessory
                ):
                    self.accessory.setCurrentIndex(i)
                    break
        self._update_portraits()

    def _on_name_changed(self):
        self.config.name = self.name.text()

    def _on_gender_changed(self):
        self.config.gender = self.gender.currentText()

    def _on_portraits_changed(self):
        self.config.portraits = self.portraits.currentData()
        self._update_portraits()

    def _on_accessory_changed(self):
        self.config.accessory = self.accessory.currentData()
        self._update_portraits()

    def _update_portraits(self):
        if data := self.portraits.currentData():
            fsid = self.service.fid_to_fsid(data, self._portrait_mode())
            rid = self.gd.key_to_rid("portraits", fsid)
        else:
            rid = None
        self.preview.set_target(rid)

    def _portrait_options(self):
        raise NotImplementedError

    def _accessory_options(self):
        raise NotImplementedError

    def _supports_accessories(self):
        raise NotImplementedError

    def _portrait_mode(self):
        raise NotImplementedError
