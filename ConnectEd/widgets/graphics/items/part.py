from typing import Self

from ....core.types import RectHandleId, DataKind

from ..properties import PropertyTextSpec, InherentProperty

class PartItemMixin:
    """Common functionality for blocks and symbols."""
    _PROPERTIES_PART = {
            "Label" : InherentProperty(
                kind   = DataKind.STR,
                worthy = lambda self: self._label != "",
                getter = lambda self: self._label,
                setter = lambda self, value: setattr(self, "_label", value)
            ),
            "Name" : InherentProperty(
                kind   = DataKind.STR,
                worthy = lambda self: self._name != "",
                getter = lambda self: self._name,
                setter = lambda self, value: setattr(self, "_name", value)
            ),
            "Path" : InherentProperty(
                kind   = DataKind.STR,
                worthy = lambda self: self._path != "",
                getter = lambda self: self._path,
                setter = lambda self, value: setattr(self, "_path", value)
            )
        }
    _PROPERTY_TEXTS = {
        "Label" : PropertyTextSpec(
            cleat=RectHandleId.TOP_LEFT, origin=RectHandleId.BOTTOM_LEFT
        ),
        "Name"  : PropertyTextSpec(
            cleat=RectHandleId.BOTTOM_LEFT, origin=RectHandleId.TOP_LEFT
        )
    }

    # instance attributes
    _label : str
    _name  : str
    _path  : str

    def initPart(self : Self) -> None:
        self._label = ""
        self._name = ""
        self._path = ""

    def label(self : Self) -> str:
        return self._label

    def setLabel(self : Self, label : str) -> None:
        self._label = label

    def name(self : Self) -> str:
        return self._name

    def setName(self : Self, name : str) -> None:
        self._name = name

    def path(self : Self) -> str:
        return self._path

    def setPath(self : Self, path : str) -> None:
        self._path = path
