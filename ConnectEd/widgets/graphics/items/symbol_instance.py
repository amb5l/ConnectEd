from typing import Self

from PyQt6.QtCore    import QRectF
from PyQt6.QtGui     import QPainterPath

from ....app import logger

from ....core.check import checked
from ....core.types import DataKind, RectHandleId
from ....core.utils import registerClass

from ..properties import PropertyTextSpec, InherentProperty

from ..scenes.symbol import SymbolScene

from .base_rect        import BaseRectangleItem
from .symbol_container import SymbolContainer

from .mixin.transform import ItemTransformMixin


class BaseSymbolInstanceItem(BaseRectangleItem):
    # class attributes
    _PROPERTIES_NAME = \
        {
            "Name" : InherentProperty(
                kind   = DataKind.STR,
                getter = lambda self: self._symbol.name(),
                setter = lambda self, value: self._symbol.setName(value)
            )
        }

    # instance attributes
    _symbol : SymbolScene
    _brect  : QRectF
    _hshape : QPainterPath

    @checked
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
            self.initProperty(name, container.properties.value(name))
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
    _PROPERTIES_LABEL = \
        {
            "Label" : InherentProperty(
                kind   = DataKind.STR,
                getter = lambda self: self.label(),
                setter = lambda self, value: self.setLabel(value)
            )
        }
    _PROPERTIES = \
        _PROPERTIES_LABEL | \
        BaseSymbolInstanceItem._PROPERTIES_NAME | \
        ItemTransformMixin._PROPERTIES_POS | \
        ItemTransformMixin._PROPERTIES_ROTATE
    _PROPERTY_TEXTS = {
        "Label" : PropertyTextSpec(
            cleat=RectHandleId.TOP_LEFT, origin=RectHandleId.BOTTOM_LEFT
        ),
        "Name"  : PropertyTextSpec(
            cleat=RectHandleId.BOTTOM_LEFT, origin=RectHandleId.TOP_LEFT
        )
    }

    # instance attributes
    _label  : str

    def label(self : Self) -> str:
        return self._label

    @checked
    def setLabel(self : Self, label : str) -> None:
        self._label = label
        self.properties.signalChanges("Label")
