from typing import Self

from ....core.check import checked
from ....core.types import RectHandleId, DataKind

from ..properties import PropertyTextSpec, InherentProperty

class PartItemMixin:
    """Common functionality for blocks and symbols."""
    _PROPERTIES_PART = {
            "Label" : InherentProperty(
                kind   = DataKind.STR,
                worthy = lambda self: self.label() != "",
                getter = lambda self: self.label(),
                setter = lambda self, value: self.setLabel(value)
            ),
            "Name" : InherentProperty(
                kind   = DataKind.STR,
                worthy = lambda self: self.name() != "",
                getter = lambda self: self.name(),
                setter = lambda self, value: self.setName(value)
            ),
            "Path" : InherentProperty(
                kind   = DataKind.STR,
                worthy = lambda self: self.path() != "",
                getter = lambda self: self.path(),
                setter = lambda self, value: self.setPath(value)
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

    @checked
    def initPart(self : Self) -> None:
        self._label = ""
        self._name = ""
        self._path = ""

    def label(self : Self) -> str:
        return self._label

    def setLabel(self : Self, label : str) -> None:
        self._label = label
        self.properties.signalChanges("Label")

    def name(self : Self) -> str:
        return self._name

    @checked
    def setName(self : Self, name : str) -> None:
        self._name = name
        self.properties.signalChanges("Name")

    def path(self : Self) -> str:
        return self._path

    @checked
    def setPath(self : Self, path : str) -> None:
        self._path = path
        self.properties.signalChanges("Path")
