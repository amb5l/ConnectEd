from typing import Self

from ...items.base_pin import BasePinItem


class DrawingSceneNetlistMixin:
    def getPinNetName(self : Self, pin : BasePinItem) -> str:
        return "TODO"
