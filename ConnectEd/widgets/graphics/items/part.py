from __future__ import annotations

from typing import Self

from ....core.check import checked
from ....core.types import RectHandleId, DataKind

from ..properties   import PropertySpec, PropertiesMixin

from .label import LabelSpec


class PartItemMixin:
    """Common functionality for blocks and symbols."""
    _PROPERTIES_PART = {
        "Reference" : PropertySpec["PartItemMixin"](
            kind   = DataKind.STR,
            getter = lambda self: self.reference(),
            setter = lambda self, value: self.setReference(value)
        ),
        "Name" : PropertySpec["PartItemMixin"](
            kind   = DataKind.STR,
            getter = lambda self: self.name(),
            setter = lambda self, value: self.setName(value)
        )
    }
    _LABELS = {
        "Reference" : LabelSpec(
            cleat=RectHandleId.TOP_LEFT, origin=RectHandleId.BOTTOM_LEFT
        ),
        "Name" : LabelSpec(
            cleat=RectHandleId.BOTTOM_LEFT, origin=RectHandleId.TOP_LEFT
        )
    }

    # instance attributes
    _reference : str
    _name      : str

    @checked
    def initPart(self : Self) -> None:
        self._reference = ""
        self._name = ""

    def reference(self : Self) -> str:
        return self._reference

    @checked
    def setReference(self : Self, reference : str) -> None:
        self._reference = reference
        if isinstance(self, PropertiesMixin):
            self.properties["Reference"].notify()

    def name(self : Self) -> str:
        return self._name

    @checked
    def setName(self : Self, name : str) -> None:
        self._name = name
        if isinstance(self, PropertiesMixin):
            self.properties["Name"].notify()
