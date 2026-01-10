from typing import Self

from PyQt6.QtCore    import QRectF
from PyQt6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget
from PyQt6.QtGui     import QPainter, QPainterPath

from ...graphics.scenes.symbol import SymbolScene

from ..properties import PropertiesMixin

from .symbol_pin import SymbolPin

from .mixin         import ItemMixin
from .mixin.pos     import ItemPosMixin
from .mixin.rotate  import ItemRotateMixin
from .mixin.line    import ItemLineMixin
from .mixin.fill    import ItemFillMixin
from .mixin.change  import ItemChangeMixin
from .mixin.clone   import ItemCloneMixin
from .mixin.xml     import ItemXmlMixin
from .mixin.menu    import ItemMenuMixin


class Symbol(
    ItemMixin,
    ItemPosMixin,
    ItemRotateMixin,
    ItemLineMixin,
    ItemFillMixin,
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

    def __init__(
        self   : Self,
        source : SymbolScene
    ) -> None:
        super().__init__()
        self._source = source
        self._brect = QRectF()
        self._hshape = QPainterPath()
        self.onSourceChange()

    def onSourceChange(self : Self) -> None:
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
            if not isinstance(item, SymbolPin):
                continue
            item.setParentItem(None)
            scene.removeItem(item)
        # add new pins
        for item in self._source.items():
            if not isinstance(item, SymbolPin):
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
            if isinstance(item, SymbolPin):
                continue
            item.paint(painter, option, widget)
