import datetime

from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QHeaderView

from paragon.model.store_manager_model import StoreManagerModel, StoreManagerProxyModel
from paragon.ui.views.ui_store_manager import Ui_StoreManager


class StoreManager(Ui_StoreManager):
    def __init__(self, ms, gs):
        super().__init__()

        self.config = ms.config
        self.gs = gs
        self.model = StoreManagerModel(gs.data)
        self.proxy_model = StoreManagerProxyModel()
        self.timer = QTimer(self)

        self.proxy_model.setSourceModel(self.model)
        self.table.setModel(self.proxy_model)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.auto_refresh_check.setChecked(self.config.store_manager_auto_refresh)
        self.timer.setInterval(5000)  # 5 seconds
        if self.config.store_manager_auto_refresh:
            self.timer.start()

        self.refresh_button.clicked.connect(self._on_refresh_clicked)
        self.auto_refresh_check.stateChanged.connect(self._on_auto_refresh_checked)
        self.timer.timeout.connect(self._on_refresh_clicked)

    def closeEvent(self, event) -> None:
        self.timer.stop()

    def showEvent(self, event) -> None:
        if self.config.store_manager_auto_refresh:
            self.timer.start()

    def _on_refresh_clicked(self):
        self.model.refresh()
        current_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
        self.status_bar.showMessage(f"Refreshed at {current_time}")
        print("Refreshed")

    def _on_auto_refresh_checked(self):
        auto_refresh = self.auto_refresh_check.isChecked()
        self.config.store_manager_auto_refresh = auto_refresh
        if auto_refresh:
            self.timer.start()
            self.status_bar.showMessage("Enabled auto refresh.")
        else:
            self.timer.stop()
            self.status_bar.showMessage("Disabled auto refresh.")
