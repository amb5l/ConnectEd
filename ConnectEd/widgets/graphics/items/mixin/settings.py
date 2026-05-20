from typing import Self

from .....app import settings

from .....core.check import checked

class ItemSettingsMixin:
    @checked
    def initSettings(self : Self) -> None:
        if hasattr(self, "onSettingsChanged"):
            settings().changed.connect(self.onSettingsChanged)

    def onSettingsChanged(self : Self) -> None:
        if hasattr(self, "onSceneChanged"):
            self.onSceneChanged()
