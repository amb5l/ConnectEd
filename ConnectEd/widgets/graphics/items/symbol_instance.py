from typing import Self

from PyQt6.QtCore    import QRectF
from PyQt6.QtGui     import QPainterPath

from ....app import logger

from ....core.utils import registerClass

from ..properties import PropertyTextSpec, PropertySpec

from ..scenes.symbol import SymbolScene

from .base_rect        import BaseRectangleItem
from .symbol_container import SymbolContainer

from .mixin.pos        import ItemPosMixin
from .mixin.rotate     import ItemRotateMixin


class BaseSymbolInstanceItem(ItemPosMixin, ItemRotateMixin, BaseRectangleItem):
    # class attributes
    _INHERENT_PROPERTIES_NAME = \
        {
            "Name" : PropertySpec(
                getter = lambda self: self._symbol.name(),
                setter = lambda self, value: self._symbol.setName(value),
                text   = PropertyTextSpec("Bottom Left")
            )
        }

    # instance attributes
    _symbol : SymbolScene
    _brect  : QRectF
    _hshape : QPainterPath

    def __init__(self : Self, symbol : SymbolScene) -> None:
        super().__init__()
        self._symbol = symbol
        self._label = "U?"

    def _loadSymbol(self : Self) -> None:
        symbol = self._symbol
        items = symbol.items()
        # get container
        containers = [item for item in items if isinstance(item, SymbolContainer)]
        if len(containers) == 0:
            logger().error("SymbolInstance: no symbol container found")
            return
        if len(containers) > 1:
            logger().warning("SymbolInstance: multiple symbol containers found")
        container = containers[0]
        # set bounding rect and shape
        self._brect = QRectF()
        self._brect.setPos(container.pos())
        self._brect.setSize(container.rect().size())
        self._hshape = QPainterPath()
        self._hshape.addRect(self._brect)
        # load custom properties
        for name in container.getCustomPropertyNames():
            self.initProperty(name, container.getPropertyValue(name))
        # load graphics: clone scene items as children here
        _allowed_classes = {}
        registerClass( _allowed_classes , "SymbolLine"      )
        registerClass( _allowed_classes , "SymbolRectangle" )
        registerClass( _allowed_classes , "SymbolEllipse"   )
        registerClass( _allowed_classes , "SymbolPolyline"  )
        registerClass( _allowed_classes , "SymbolText"      )
        registerClass( _allowed_classes , "SymbolTextBlock" )
        for item in items:
            if not isinstance(item, tuple(_allowed_classes.values())):
                continue
            clone = item.clone()
            clone.setParentItem(self)

    def boundingRect(self : Self) -> QRectF:
        return self._brect

    def shape(self : Self) -> QPainterPath:
        return self._hshape


class SymbolInstanceItem(BaseSymbolInstanceItem):
    # class attributes
    _INHERENT_PROPERTIES_LABEL = \
        {
            "Label" : PropertySpec(
                getter = lambda self: self._label,
                setter = lambda self, value: setattr(self, "_label", value),
                text   = PropertyTextSpec("Top Left")
            )
        }
    _INHERENT_PROPERTIES = \
        _INHERENT_PROPERTIES_LABEL | \
        BaseSymbolInstanceItem._INHERENT_PROPERTIES_NAME | \
        ItemPosMixin._INHERENT_PROPERTIES_POS | \
        ItemRotateMixin._INHERENT_PROPERTIES_ROTATE

    # instance attributes
    _label  : str
