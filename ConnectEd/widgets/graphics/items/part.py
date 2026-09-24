from __future__ import annotations

from typing import Self

from ....core.check import checked
from ....core.types import RectHandleId, DataKind

from ..properties import PropertySpec, PropertiesMixin

from .property_text import PropertyTextSpec


class PartItemMixin:
    """Common functionality for blocks and symbols."""
    _PROPERTIES_PART = {
            "Label" : PropertySpec["PartItemMixin"](
                kind   = DataKind.STR,
                getter = lambda self: self.label(),
                setter = lambda self, value: self.setLabel(value)
            ),
            "Name" : PropertySpec["PartItemMixin"](
                kind   = DataKind.STR,
                getter = lambda self: self.name(),
                setter = lambda self, value: self.setName(value)
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

    @checked
    def initPart(self : Self) -> None:
        self._label = ""
        self._name = ""

    def label(self : Self) -> str:
        return self._label

    @checked
    def setLabel(self : Self, label : str) -> None:
        self._label = label
        if isinstance(self, PropertiesMixin):
            self.properties["Label"].notify()

    def name(self : Self) -> str:
        return self._name

    @checked
    def setName(self : Self, name : str) -> None:
        self._name = name
        if isinstance(self, PropertiesMixin):
            self.properties["Name"].notify()
