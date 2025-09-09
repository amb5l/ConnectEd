from typing import Self, Optional, Any

from PyQt6.QtCore    import QLineF
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsPathItem, QGraphicsLineItem

from .. import SignalDirection

from ..mixin.loc    import ElementLocMixin
from ..mixin.line   import ElementLineMixin

from .node     import Node
from .port_pin import PortPinMixin, PortPinText

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...scenes.drawing import DrawingScene


_PIN_LEN = 10 # documentation - DO NOT CHANGE


class PinArrow(ElementLineMixin, QGraphicsPathItem):

    # instance attributes
    _direction : SignalDirection

    def __init__(self : Self, parent : Optional[QGraphicsItem] = None) -> None:
        QGraphicsPathItem.__init__(self, parent)
        self.initLine()
        self._direction = SignalDirection.BI

    def itemChange(
        self   : Self,
        change : QGraphicsItem.GraphicsItemChange,
        value  : Any
    ) -> Any:
        match change:
            case QGraphicsItem.GraphicsItemChange.ItemSceneChange:
                self._setPath(value)
        return super().itemChange(change, value)

    @property
    def direction(self : Self) -> SignalDirection:
        return self._direction

    @direction.setter
    def direction(self : Self, value : SignalDirection) -> None:
        self._direction = value
        self._setPath(self.scene())

    def _setPath(self : Self, scene : "DrawingScene") -> None:
        if scene is not None \
        and hasattr(scene, 'paths') \
        and self.__class__.__name__ in scene.paths \
        and self._direction.value in scene.paths[self.__class__.__name__]:
            path = scene.paths[self.__class__.__name__][self._direction.value]
            self.setPath(path)


class PinNode(Node):
    pass


class PinName(PortPinText):
    pass


class PinComment(PortPinText):
    pass


class Pin(ElementLocMixin, PortPinMixin, QGraphicsLineItem):
    # class attributes
    _PROPERTY_SPECS = \
        ElementLocMixin._PROPERTY_SPECS_LOC | \
        PortPinMixin._PROPERTY_SPECS

    @classmethod
    def _getArrowClass(cls) -> type[PinArrow]:
        return PinArrow

    @classmethod
    def _getNodeClass(cls) -> type[PinNode]:
        return PinNode

    @classmethod
    def _getNameClass(cls) -> type[PinName]:
        return PinName

    @classmethod
    def _getCommentClass(cls) -> type[PinComment]:
        return PinComment

    def __init__(self : Self, parent : Optional[QGraphicsItem] = None) -> None:
        QGraphicsLineItem.__init__(self, parent)
        self.initPortPin()
        line = QLineF(-_PIN_LEN, 0, 0, 0)
        self.setLine(line)
        self._node.setPos(-_PIN_LEN, 0)
        self._arrow = self._getArrowClass()(self)

    @property
    def direction(self : Self) -> SignalDirection:
        return super().direction

    @direction.setter
    def direction(self : Self, value : SignalDirection) -> None:
        super(Pin, Pin).direction.__set__(self, value)
        self._arrow.direction = value
