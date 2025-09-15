from typing import Self, Optional

from PyQt6.QtWidgets import QWidget, QGraphicsItem, QGraphicsPathItem, \
                            QStyleOptionGraphicsItem, QStyle
from PyQt6.QtGui     import QPainter

from .....app import settings

from ..mixin.pos  import ElementPosMixin
from ..mixin.fill import ElementFillMixin

from .node     import Node
from .port_pin import PortPinText, PortPinMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...scenes.drawing import DrawingScene
    from .. import SignalDirection


class PortNode(Node):
    pass


class PortName(PortPinText):
    pass


class PortComment(PortPinText):
    pass


class Port(ElementPosMixin, ElementFillMixin, PortPinMixin, QGraphicsPathItem):
    # class attributes
    _NAME_OFFSET = 2
    _PROPERTY_SPECS = \
        ElementPosMixin._PROPERTY_SPECS_POS | \
        PortPinMixin._PROPERTY_SPECS | \
        ElementFillMixin._PROPERTY_SPECS_FILL

    @classmethod
    def _getNodeClass(cls) -> type[PortNode]:
        return PortNode

    @classmethod
    def _getNameClass(cls) -> type[PortName]:
        return PortName

    @classmethod
    def _getCommentClass(cls) -> type[PortComment]:
        return PortComment

    def __init__(self : Self, parent : Optional[QGraphicsItem] = None) -> None:
        QGraphicsPathItem.__init__(self, parent)
        self.initPortPin()
        self.onSettingsChange()

    def onSettingsChange(self : Self) -> None:
        size = settings().getTheme("elements/Port/size")
        self.getAnchorPoint("Name").setPos(size + self._NAME_OFFSET, 0)

    def onSceneChange(self : Self, scene : "DrawingScene") -> None:
        self._setPath(scene)

    @property
    def direction(self : Self) -> "SignalDirection":
        return super().direction

    @direction.setter
    def direction(self : Self, value : "SignalDirection") -> None:
        super(Port, Port).direction.__set__(self, value)
        self._setPath(self.scene())

    def _setPath(self : Self, scene : "DrawingScene") -> None:
        scene : "DrawingScene" = self.scene()
        if scene is not None \
        and self.__class__.__name__ in scene.paths \
        and self._direction.value in scene.paths[self.__class__.__name__]:
            path = scene.paths[self.__class__.__name__][self._direction.value]
            self.setPath(path)

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : Optional[QWidget] = None
    ) -> None:
        option.state &= ~QStyle.StateFlag.State_Selected
        QGraphicsPathItem.paint(self, painter, option, widget)
