from typing import Self

from PyQt6.QtWidgets import QGraphicsItem

from .....app import settings

from .....core.check import checked

from ..protocols import OnSceneChangedProtocol


class ItemSettingsMixin:
    @checked
    def initSettings(self : Self) -> None:
        settings().changed.connect(self.onSettingsChanged)

    def onSettingsChanged(self : Self) -> None:
        from ...scenes.diagram import DiagramScene
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        if  isinstance(scene := self.scene(), DiagramScene) \
        and isinstance(self, OnSceneChangedProtocol):
            self.onSceneChanged(scene)
