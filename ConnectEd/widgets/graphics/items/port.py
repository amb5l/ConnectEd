from typing import Self

from PyQt6.QtWidgets import QWidget, QGraphicsItem, QGraphicsPathItem, \
                            QStyleOptionGraphicsItem, QStyle
from PyQt6.QtGui     import QPainter

from ....app import settings

from ..scenes.drawing.cmd import cmdRotate

from .mixin.pos  import ElementPosMixin
from .mixin.fill import ElementFillMixin

from .port_pin import PortPinText, PortPinMixin
from .entry    import Entry

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing import DrawingView
    from ..scenes.drawing import DrawingScene
    from . import SignalDirection


class PortEntry(Entry):
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
    def _getEntryClass(cls) -> type[PortEntry]:
        return PortEntry

    @classmethod
    def _getNameClass(cls) -> type[PortName]:
        return PortName

    @classmethod
    def _getCommentClass(cls) -> type[PortComment]:
        return PortComment

    def __init__(
        self   : Self,
        parent : QGraphicsItem | None = None,
        bare   : bool = False
    ) -> None:
        QGraphicsPathItem.__init__(self, parent)
        self.initPortPin(bare)

    def onSettingsChange(self : Self) -> None:
        size = settings().get("theme/elements/Port/size")
        self.getAnchorPoint("Name").setPos(size + self._NAME_OFFSET, 0)

    def onSceneChange(self : Self, scene : "DrawingScene") -> None:
        self._setPath(scene)

    def setRotation(self : Self, angle : float) -> None:
        super().setRotation(angle)
        for child in self.childItems(): # anchor points
            for grandchild in child.childItems(): # property texts
                if hasattr(grandchild, 'compensateRotation'):
                    grandchild.compensateRotation(angle)

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
        widget  : QWidget | None = None
    ) -> None:
        option.state &= ~QStyle.StateFlag.State_Selected
        QGraphicsPathItem.paint(self, painter, option, widget)

    def getMenuItems(self : Self) -> list[str]:
        return ["Rotate CW", "Rotate CCW", "-", "Edit"]

    def ctxMenuRotateCW(
        self    : Self,
        _checked : bool,
        view    : "DrawingView"
    ) -> None:
        scene : "DrawingScene" = self.scene()
        scene.undo_stack.push(cmdRotate(scene, [self], +90))

    def ctxMenuRotateCCW(
        self    : Self,
        _checked : bool,
        view    : "DrawingView"
    ) -> None:
        scene : "DrawingScene" = self.scene()
        scene.undo_stack.push(cmdRotate(scene, [self], -90))

    def ctxMenuEdit(
        self     : Self,
        _checked : bool,
        view     : "DrawingView"
    ) -> None:
        view.editPort(self)
