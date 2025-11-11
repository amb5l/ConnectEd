from typing import Self

from .items.anchor_point import AnchorPoint


class AnchorPointsMixin:
    @classmethod
    def getAnchorPointNames(cls : type[Self]) -> list[str]:
        raise NotImplementedError("Subclass must implement this method")

    # instance attributes
    _anchor_points : dict[str, "AnchorPoint"]

    def initAnchorPoints(self : Self) -> None:
        raise NotImplementedError("Subclass must implement this method")

    def getAnchorPoint(self : Self, name : str) -> "AnchorPoint":
        return self._anchor_points[name]
