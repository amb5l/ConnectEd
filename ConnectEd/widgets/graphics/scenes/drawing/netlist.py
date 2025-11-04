from typing import Self

from ...items.base_pin import BasePin


class DrawingSceneNetlistMixin:
    def getPinNetName(self : Self, pin : BasePin) -> str:
        return "TODO"
