from __future__ import annotations

from typing import Self

from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsLineItem, QGraphicsItem

from ....app import settings

from ....core.check import checked
from ....core.defs  import WIDTH
from ....core.types import Direction, DataKind
from ....core.utils import qtItemClass

from ..properties import InherentProperty

from ..scenes import withScene

from .role      import FunctionalItem
from .node      import FixedNodeItem
from .protocols import SetPenProtocol

from .mixin.names     import ItemNamesMixin
from .mixin.primary   import PrimaryItemMixin
from .mixin.transform import ItemTransformMixin
from .mixin.paint     import ItemPaintMixin
from .mixin.change    import ItemChangeMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.diagram import DiagramScene


class PortPinArrowItem(
    ItemNamesMixin,
    ItemPaintMixin,
    ItemChangeMixin,
    QGraphicsPathItem
):
    @checked
    def __init__(self : Self, parent : QGraphicsItem | None = None) -> None:
        super().__init__(parent)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

    def onSelectionChanged(self : Self, selected : bool) -> None:
        parent = self.parentItem()
        if parent is not None:
            parent.setSelected(selected)


class PortPinMixin(FunctionalItem, PrimaryItemMixin):
    """
    Mixin for ports and gate/block/symbol pins.
    """

    # class attributes
    _NODE_POS   : int
    _ARROW_CLS  : type[PortPinArrowItem]
    _ARROW_POS  : int
    _PROPERTIES = \
        {
            "Name" : InherentProperty["PortPinMixin"](
                kind   = DataKind.STR,
                getter = lambda self: self.name(),
                setter = lambda self, value: self.setName(value),
            ),
            "Dir" : InherentProperty["PortPinMixin"](
                kind   = DataKind.DIRECTION,
                getter = lambda self: self.direction(),
                setter = lambda self, value: self.setDirection(value)
            ),
            "Comment" : InherentProperty["PortPinMixin"](
                kind   = DataKind.STR,
                worthy = lambda self: self.comment() != "",
                getter = lambda self: self.comment(),
                setter = lambda self, value: self.setComment(value)
            )
        }

    # instance attributes
    _node      : FixedNodeItem
    _arrow     : PortPinArrowItem
    _name      : str
    _direction : Direction
    _comment   : str
    _bus       : bool

    @checked
    def __init__(
        self   : Self,
        parent : QGraphicsItem | None = None,
        fresh  : bool = True
    ) -> None:
        if not isinstance(self, QGraphicsItem): raise TypeError("Bad host")
        if not isinstance(parent, QGraphicsItem): raise TypeError("Bad parent")
        qtItemClass(self).__init__(parent)
        # node
        self._node = FixedNodeItem(parent=self)
        self._node.setPos(self._NODE_POS, 0)
        # arrow
        self._arrow = self._ARROW_CLS(self)
        self._arrow.setPos(self._ARROW_POS, 0)
        # attributes that properties will access
        self._name      = ""
        self._direction = Direction.IN
        self._comment   = ""
        self._bus       = False
        # initialize the item
        self.initItem(fresh)

    def onSettingsChanged(self : Self) -> None:
        if (scene := self.scene()) is not None:
            self.onSceneChanged(scene)

    @checked
    def onSceneChanged(self : Self, scene : DiagramScene | None) -> None:
        if scene is None:
            return
        self._updateGraphics(scene)
        self._updatePen(scene)
        self._updateArrowPath(scene)
        self._updateArrowPenBrush(scene)
        self._updateNameHandle()
        for handle in self._handles.values():
            handle.onSceneOrientationChanged()

    @checked
    def onSelectionChanged(self : Self, selected : bool) -> None:
        scene = self.scene()
        if scene is None:
            return
        self._updatePen(scene)
        self._updateArrowPenBrush(scene)
        self._updateNameHandle()
        self._node.setSelected(selected)
        self._arrow.setSelected(selected)

    def node(self : Self) -> FixedNodeItem:
        return self._node

    def name(self : Self) -> str:
        return self._name

    @checked
    def setName(self : Self, value : str) -> None:
        self._name = value
        self._bus = ":" in value
        if scene := self.scene():
            self._updatePen(scene)  # because name => bus => pin width
        self.properties.signalChanges("Name")

    def direction(self : Self) -> Direction:
        return self._direction

    @checked
    def setDirection(self : Self, value : Direction) -> None:
        self._direction = value
        self.properties.signalChanges("Dir")
        if scene := self.scene():
            self._updateArrowPath(scene)

    def comment(self : Self) -> str:
        return self._comment

    @checked
    def setComment(self : Self, value : str) -> None:
        self._comment = value
        self.properties.signalChanges("Comment")

    def bus(self : Self) -> bool:
        return self._bus

    def _resourceKey(self : Self) -> tuple[bool, bool]:
        if not isinstance(self, QGraphicsItem): raise TypeError("Bad host")
        return (self.bus(), self.isSelected())

    def _resourceKeyDefault(self : Self) -> tuple[bool, bool]:
        return (False, False)

    def _updateGraphics(self : Self, scene : DiagramScene) -> None:
        raise NotImplementedError("Subclasses must implement this method")

    def _updatePen(
        self  : Self,
        scene : DiagramScene
    ) -> None:
        if not isinstance(self, QGraphicsItem): raise TypeError("Bad host")
        if not isinstance(self, SetPenProtocol): raise TypeError("Bad host")
        key = (self.bus(), self.isSelected())
        self.setPen(scene.resources.pen(self.resourcesName(), key))

    def _updateArrowPath(self : Self, scene : DiagramScene) -> None:
        self._arrow.setPath(scene.resources.path(
            self._arrow.resourcesName(), self._direction
        ))

    def _updateArrowPenBrush(
        self  : Self,
        scene : DiagramScene
    ) -> None:
        if not isinstance(self, QGraphicsItem): raise TypeError("Bad host")
        key = self.isSelected()
        self._arrow.setPen(scene.resources.pen(self._arrow.resourcesName(), key))
        self._arrow.setBrush(scene.resources.brush(self._arrow.resourcesName(), key))

    def _updateNameHandle(self : Self) -> None:
        raise NotImplementedError("Subclasses must implement this method")


class PortPinLineItem(PortPinMixin, QGraphicsLineItem):
    """
    Base class for ports and block pins.
    """

    def _updateGraphics(self : Self, scene : DiagramScene) -> None:
        self.setLine(scene.resources.line(self.resourcesName()))

    def _updateNameHandle(self : Self) -> None:
        """Place name handle beside arrow."""
        name_handle = self.getHandle("Name")
        x = self._arrow.pos().x() + self._arrow.boundingRect().right() + WIDTH
        name_handle.setX(x)


class PortPinPathItem(PortPinMixin, QGraphicsPathItem):
    """
    Base class for gate and symbol pins.
    """

    # class attributes
    _PROPERTIES = \
        PortPinMixin._PROPERTIES | \
        {
            "Dot" : InherentProperty["PortPinPathItem"](
                kind   = DataKind.BOOL,
                getter = lambda self: self.dot(),
                setter = lambda self, value: self.setDot(value)
            ),
            "Clock" : InherentProperty["PortPinPathItem"](
                kind   = DataKind.BOOL,
                getter = lambda self: self.clock(),
                setter = lambda self, value: self.setClock(value)
            )
        } | \
        ItemTransformMixin._PROPERTIES_NO_ORIGIN

    # instance attributes
    _dot   : bool = False
    _clock : bool = False

    def dot(self : Self) -> bool:
        return self._dot

    @checked
    def setDot(self : Self, value : bool) -> None:
        self._dot = value
        self._updateGraphics()
        self.properties.signalChanges("Dot")

    def clock(self : Self) -> bool:
        return self._clock

    @checked
    def setClock(self : Self, value : bool) -> None:
        self._clock = value
        self._updateGraphics()
        self._updateNameHandle()
        self.properties.signalChanges("Clock")

    @withScene
    def _updateGraphics(self : Self, scene : DiagramScene) -> None:
        key = (self._clock, self._dot)
        self.setPath(scene.resources.path(self.resourcesName(), key))

    def _updateNameHandle(self : Self) -> None:
        """Allow for clock symbol."""
        settings_path = f"theme/items/{self.settingsName()}/pin"
        x = 0
        # allow for clock symbol
        if self._clock:
            x += settings().get(f"{settings_path}/clock/size")
        # allow for pen width
        x += settings().get(f"{settings_path}/wire/line/width") / 2
        # standard offset
        x += WIDTH
        # apply to name handle
        name_handle = self.getHandle("Name")
        name_handle.setX(x)
