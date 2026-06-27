from typing import Self

from ....core.check import checked
from ....core.types import RectHandleId, DataKind

from ..properties import PropertiesMixin, PropertyTextSpec, InherentProperty

MixinSelf = Self | PropertiesMixin

class PartItemMixin:
    """Common functionality for blocks and symbols."""
    _PROPERTIES_PART = {
            "Label" : InherentProperty["PartItemMixin"](
                kind   = DataKind.STR,
                getter = lambda self: self.label(),
                setter = lambda self, value: self.setLabel(value)
            ),
            "Name" : InherentProperty["PartItemMixin"](
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
    def initPart(self : MixinSelf) -> None:
        self._label = ""
        self._name = ""

    def label(self : MixinSelf) -> str:
        return self._label

    @checked
    def setLabel(self : MixinSelf, label : str) -> None:
        self._label = label
        self.properties.signalChanges("Label")

    def name(self : MixinSelf) -> str:
        return self._name

    @checked
    def setName(self : MixinSelf, name : str) -> None:
        self._name = name
        self.properties.signalChanges("Name")
