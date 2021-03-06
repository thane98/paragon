from typing import Optional, List

from paragon.ui.renderers.fates_standard_dialogue_renderer import (
    FatesStandardDialogueRenderer,
)

from paragon.ui.renderers.fates_mini_dialogue_renderer import FatesMiniDialogueRenderer

from paragon.model.dialogue_snapshot import DialogueSnapshot
from paragon.model.game import Game
from paragon.ui.renderers.awakening_standard_dialogue_renderer import (
    AwakeningStandardDialogueRenderer,
)
from paragon.ui.renderers.sov_mini_dialogue_renderer import SOVMiniDialogueRenderer
from paragon.ui.renderers.sov_standard_dialogue_renderer import (
    SOVStandardDialogueRenderer,
)
from paragon.ui.views.ui_dialogue_player import Ui_DialoguePlayer


class DialoguePlayer(Ui_DialoguePlayer):
    def __init__(self):
        super().__init__()
        self.service = None
        self.sprite_animation_svc = None
        self.game = Game.FE15
        self.snapshots: List[DialogueSnapshot] = []
        self.current: Optional[int] = None

        self.refresh_buttons()

        self.background_box.currentIndexChanged.connect(self.redraw)
        self.window_type_box.currentIndexChanged.connect(self.redraw)
        self.begin_button.clicked.connect(self._on_begin)
        self.end_button.clicked.connect(self._on_end)
        self.next_button.clicked.connect(self._on_next)
        self.previous_button.clicked.connect(self._on_previous)

    def _on_begin(self):
        self._set_current(0)

    def _on_end(self):
        self._set_current(len(self.snapshots) - 1)

    def _on_next(self):
        self._set_current(self.current + 1)

    def _on_previous(self):
        self._set_current(self.current - 1)

    def _set_current(self, index):
        self.current = index
        self.redraw()
        self.refresh_buttons()

    def set_service(self, service, sprite_animation_svc):
        self.service = service
        self.sprite_animation_svc = sprite_animation_svc

    def set_backgrounds(self, backgrounds):
        self.background_box.clear()
        for name, pixmap in backgrounds:
            self.background_box.addItem(name, pixmap)

    def set_windows(self, sets):
        self.window_type_box.clear()
        for k, v in sets.items():
            self.window_type_box.addItem(k, v)

    def set_game(self, game: Game):
        self.game = game
        self.redraw()

    def set_snapshots(self, snapshots: List[DialogueSnapshot]):
        self.snapshots = snapshots
        self.current = 0 if self.snapshots else None
        self.redraw()
        self.refresh_buttons()

    def refresh_buttons(self):
        self.begin_button.setEnabled(len(self.snapshots) > 0)
        self.end_button.setEnabled(len(self.snapshots) > 0)
        self.next_button.setEnabled(
            self.current is not None and self.current < len(self.snapshots) - 1
        )
        self.previous_button.setEnabled(self.current is not None and self.current > 0)

    def redraw(self):
        # Clear out the old scene.
        self.scene.clear()

        # Draw the background.
        background = self.background_box.currentData()
        if background:
            self.scene.addPixmap(background)

        # Get the window set.
        window_set = self.window_type_box.currentData()
        if not window_set:
            return  # TODO: Issue a warning maybe?

        # Render.
        if self.current is not None:
            current = self.snapshots[self.current]
            if self.game == Game.FE15 and current.conversation_type == 0:
                self.renderer = SOVMiniDialogueRenderer()
            elif self.game == Game.FE15:
                self.renderer = SOVStandardDialogueRenderer()
            elif self.game == Game.FE14 and current.conversation_type == 0:
                self.renderer = FatesMiniDialogueRenderer()
            elif self.game == Game.FE14:
                self.renderer = FatesStandardDialogueRenderer()
            elif self.game == Game.FE13:
                self.renderer = AwakeningStandardDialogueRenderer()
            else:
                raise NotImplementedError(
                    "No renderer available for current game / type."
                )
            self.renderer.render(
                self.scene,
                window_set,
                self.service,
                self.sprite_animation_svc,
                current,
            )
