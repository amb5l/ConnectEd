from typing import Self

from PyQt6.QtCore    import QLineF
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsPathItem, QGraphicsLineItem, \
                            QStyleOptionGraphicsItem, QWidget, QStyle
from PyQt6.QtGui     import QPainter

from . import SignalDirection

from .mixin.loc    import ElementLocMixin
from .mixin.change import ElementChangeMixin
from .mixin.line   import ElementLineMixin
from .mixin.fill   import ElementFillMixin

from .port_pin import PortPinMixin, PortPinText
from .entry    import Entry

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.drawing import DrawingScene


_PIN_LEN = 10 # documentation - DO NOT CHANGE


class PinArrow(
    ElementChangeMixin,
    ElementLineMixin,
    ElementFillMixin,
    QGraphicsPathItem
):

    # instance attributes
    _direction : SignalDirection

    def __init__(self : Self, parent : QGraphicsItem | None = None) -> None:
        QGraphicsPathItem.__init__(self, parent)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.initLine()
        self.initFill()
        self._direction = SignalDirection.BI

    def onSceneChange(self : Self, scene : "DrawingScene") -> None:
        self._setPath(scene)

    def onSelectionChange(self : Self, selected : bool) -> None:
        parent = self.parentItem()
        if parent and parent.isSelected() != selected:
            parent.setSelected(selected)

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

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget | None = None
    ) -> None:
        option.state &= ~QStyle.StateFlag.State_Selected
        QGraphicsPathItem.paint(self, painter, option, widget)


class PinEntry(Entry):
    pass


class PinName(PortPinText):
    pass


class PinComment(PortPinText):
    pass


class Pin(PortPinMixin, QGraphicsLineItem):
    @classmethod
    def _getArrowClass(cls) -> type[PinArrow]:
        return PinArrow

    @classmethod
    def _getEntryClass(cls) -> type[PinEntry]:
        return PinEntry

    @classmethod
    def _getNameClass(cls) -> type[PinName]:
        return PinName

    @classmethod
    def _getCommentClass(cls) -> type[PinComment]:
        return PinComment

    def __init__(
        self   : Self,
        parent : QGraphicsItem | None = None,
        bare   : bool = False
    ) -> None:
        QGraphicsLineItem.__init__(self, parent)
        self.initPortPin(bare)
        line = QLineF(-_PIN_LEN, 0, 0, 0)
        self.setLine(line)
        self._entry.setPos(-_PIN_LEN, 0)
        self._arrow = self._getArrowClass()(self)

    @property
    def direction(self : Self) -> SignalDirection:
        return super().direction

    @direction.setter
    def direction(self : Self, value : SignalDirection) -> None:
        super(Pin, Pin).direction.__set__(self, value)
        self._arrow.direction = value

    def onGeometryChange(self : Self) -> None:
        pass

    def onSceneChange(self : Self, scene : "DrawingScene") -> None:
        self._arrow.direction = self._direction

    def onSelectionChange(self : Self, selected : bool) -> None:
        self._arrow.setSelected(selected)
        self._entry.setSelected(selected)

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget | None = None
    ) -> None:
        option.state &= ~QStyle.StateFlag.State_Selected
        QGraphicsLineItem.paint(self, painter, option, widget)
