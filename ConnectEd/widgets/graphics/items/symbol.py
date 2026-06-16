from typing import Self

from PyQt6.QtCore    import QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsRectItem

from ..scenes.symbol import SymbolScene

from ..properties import PropertiesMixin

from .part import PartItemMixin

from .role import FunctionalItem

from .mixin              import ItemMixin
from .mixin.presentation import ItemPresentationMixin
from .mixin.select       import ItemSelectMixin
from .mixin.transform    import ItemTransformMixin
from .mixin.change       import ItemChangeMixin
from .mixin.clone        import ItemCloneMixin
from .mixin.xml          import ItemXmlMixin
from .mixin.menu         import ItemMenuMixin


class SymbolItem(
    FunctionalItem,
    ItemMixin,
    ItemTransformMixin,
    ItemPresentationMixin,
    ItemSelectMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemMenuMixin,
    PropertiesMixin,
    PartItemMixin,
    QGraphicsRectItem
):
    def _penKey(self : Self) -> tuple[bool, bool]:
        return (isinstance(self.scene(), SymbolScene), self.isSelected())

    def toXmlDefinition(self : Self, xw : QXmlStreamWriter) -> None:
        """Write a definition (include pins and graphics)."""
        pass

    def toXmlInstance(self : Self, xw : QXmlStreamWriter) -> None:
        """Write an instance (no pins or graphics)."""
        pass

    @classmethod
    def fromXmlDefinition(cls : Self, xr : QXmlStreamReader) -> Self:
        """Read a definition (include pins and graphics)."""
        pass

    @classmethod
    def fromXmlInstance(
        cls        : Self,
        definition : "SymbolItem",     # normally resides in symbol cache
        xr         : QXmlStreamReader
    ) -> Self:
        """Read an instance (pins or graphics from master)."""
        pass
