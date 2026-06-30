from __future__ import annotations

from typing import Self, cast

from PyQt6.QtWidgets import QGraphicsItem

from .....core.utils import qtItemClass

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...scenes.diagram import DiagramScene


class ItemSceneMixin:
    def scene(self : Self) -> DiagramScene | None:
        scene = qtItemClass(self).scene(cast(QGraphicsItem, self))
        if scene is None:
            return None
        from ...scenes.diagram import DiagramScene
        if not isinstance(scene, DiagramScene):
            raise TypeError("Bad scene")
        return scene
