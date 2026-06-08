from typing import Self

from PyQt6.QtCore    import QRectF
from PyQt6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget
from PyQt6.QtGui     import QPainter, QPainterPath

from ....core.check import checked

from ...graphics.scenes.symbol import SymbolScene

from ..properties import PropertiesMixin

from .symbol_pin import SymbolPinItem

from .mixin           import ItemMixin
from .mixin.transform import ItemTransformMixin
from .mixin.change    import ItemChangeMixin
from .mixin.clone     import ItemCloneMixin
from .mixin.xml       import ItemXmlMixin
from .mixin.menu      import ItemMenuMixin


class SymbolItem(
    ItemMixin,
    ItemTransformMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemXmlMixin,
    ItemMenuMixin,
    PropertiesMixin,
    QGraphicsItem
):
    _source : SymbolScene
    _brect  : QRectF
    _hshape : QPainterPath

    @checked
    def __init__(
        self   : Self,
        source : SymbolScene
    ) -> None:
        super().__init__()
        self._source = source
        self._brect = QRectF()
        self._hshape = QPainterPath()
        self.onSourceChanged()

    def onSourceChanged(self : Self) -> None:
        """Update boundary and pins from source."""
        if not isinstance(self._source, SymbolScene):
            return
        scene : "SymbolScene" = self.scene()
        # update boundary rect and hit shape
        self._brect = self._source.itemsBoundingRect()
        self._hshape.clear()
        self._hshape.addRect(self._brect)
        # delete existing pins
        for item in self.childItems():
            if not isinstance(item, SymbolPinItem):
                continue
            item.setParentItem(None)
            scene.removeItem(item)
        # add new pins
        for item in self._source.items():
            if not isinstance(item, SymbolPinItem):
                continue
            pin = item.clone()
            pin.setParentItem(self)
            scene.addItem(pin)
        # refresh connectivity
        scene.tidyConns()

    def boundingRect(self : Self) -> QRectF:
        return self._brect

    def shape(self : Self) -> QPainterPath:
        return self._hshape

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        for item in self._source.items():
            if isinstance(item, SymbolPinItem):
                continue
            item.paint(painter, option, widget)
