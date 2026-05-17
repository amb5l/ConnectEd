from typing import Self

from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsLineItem, QGraphicsItem

from ....app import settings

from ....core.defs  import WIDTH
from ....core.types import Direction, DataKind

from ..properties import PropertiesMixin, InherentProperty

from ..scenes import withScene

from .node   import FixedNodeItem

from .mixin           import ItemMixin, ItemNamesMixin
from .mixin.transform import ItemTransformMixin
from .mixin.handle    import ItemHandlesMixin
from .mixin.paint     import ItemPaintMixin
from .mixin.change    import ItemChangeMixin
from .mixin.clone     import ItemCloneMixin
from .mixin.xml       import ItemXmlMixin
from .mixin.menu      import ItemMenuMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.drawing import DrawingScene


class PortPinArrowItem(
    ItemNamesMixin,
    ItemPaintMixin,
    ItemChangeMixin,
    QGraphicsPathItem
):
    def __init__(self : Self, parent : QGraphicsItem | None = None) -> None:
        super().__init__(parent)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

    def onSelectionChange(self : Self, selected : bool) -> None:
        parent = self.parentItem()
        if parent is not None:
            parent.setSelected(selected)


class PortPinMixin(
    ItemMixin,
    ItemPaintMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemXmlMixin,
    ItemMenuMixin,
    PropertiesMixin
):
    """
    Mixin for ports and gate/block/symbol pins.
    """

    # class attributes
    _NODE_POS  : int
    _ARROW_CLS : type[PortPinArrowItem]
    _ARROW_POS : int
    _PROPERTIES = \
        {
            "Name" : InherentProperty(
                kind   = DataKind.STR,
                getter = lambda self: self._name,
                setter = lambda self, value: setattr(self, "_name", value),
            ),
            "Dir" : InherentProperty(
                kind   = DataKind.DIRECTION,
                getter = lambda self: self._direction,
                setter = lambda self, value: setattr(self, "_direction", value)
            ),
            "Comment" : InherentProperty(
                kind   = DataKind.STR,
                worthy = lambda self: self._comment != "",
                getter = lambda self: self._comment,
                setter = lambda self, value: setattr(self, "_comment", value)
            )
        }

    # instance attributes
    _node      : FixedNodeItem
    _arrow     : PortPinArrowItem
    _name      : str
    _direction : Direction
    _comment   : str
    _bus       : bool

    def __init__(
        self   : Self,
        parent : QGraphicsItem | None = None,
        fresh  : bool = True
    ) -> None:
        super().__init__(parent)
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
        self.onSceneChange()

    @withScene
    def onSceneChange(self : Self, scene : "DrawingScene") -> None:
        self._updateGraphics(scene)
        self._updatePen(scene)
        self._updateArrowPath(scene)
        self._updateArrowPenBrush(scene)
        self._updateNameHandle()

    def onSelectionChange(self : Self, selected : bool) -> None:
        scene : "DrawingScene" = self.scene()
        self._updatePen(scene)
        self._updateArrowPenBrush(scene)
        self._updateNameHandle()
        self._node.setSelected(selected)
        self._arrow.setSelected(selected)

    def name(self : Self) -> str:
        return self._name

    def setName(self : Self, value : str) -> None:
        self._name = value
        self._bus = ":" in value
        if scene := self.scene():
            self._updatePen(scene)  # because name => bus => pin width
        self.signalPropertyChanges("Name")

    def direction(self : Self) -> Direction:
        return self._direction

    def setDirection(self : Self, value : Direction) -> None:
        self._direction = value
        self.signalPropertyChanges("Dir")
        if scene := self.scene():
            self._updateArrowPath(scene)

    def comment(self : Self) -> str:
        return self._comment

    def setComment(self : Self, value : str) -> None:
        self._comment = value
        self.signalPropertyChanges("Comment")

    def bus(self : Self) -> bool:
        return self._bus

    def _updateGraphics(self : Self, scene : "DrawingScene") -> None:
        raise NotImplementedError("Subclasses must implement this method")

    def _updatePen(
        self  : Self | QGraphicsLineItem | QGraphicsPathItem,
        scene : "DrawingScene"
    ) -> None:
        key = (self.bus(), self.isSelected())
        self.setPen(scene.resources.pen(self.resourcesName(), key))

    def _updateArrowPath(self : Self, scene : "DrawingScene") -> None:
        self._arrow.setPath(scene.resources.path(
            self._arrow.resourcesName(), self._direction
        ))

    def _updateArrowPenBrush(
        self  : Self | ItemHandlesMixin,
        scene : "DrawingScene"
    ) -> None:
        key = self.isSelected()
        self._arrow.setPen(scene.resources.pen(self._arrow.resourcesName(), key))
        self._arrow.setBrush(scene.resources.brush(self._arrow.resourcesName(), key))

    def _updateNameHandle(self : Self) -> None:
        raise NotImplementedError("Subclasses must implement this method")


class PortPinLineItem(PortPinMixin, QGraphicsLineItem):
    """
    Base class for ports and block pins.
    """

    def _updateGraphics(self : Self, scene : "DrawingScene") -> None:
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
            "Dot" : InherentProperty(
                kind   = DataKind.BOOL,
                getter = lambda self: self._dot,
                setter = lambda self, value: setattr(self, "_dot", value)
            ),
            "Clock" : InherentProperty(
                kind   = DataKind.BOOL,
                getter = lambda self: self._clock,
                setter = lambda self, value: setattr(self, "_clock", value)
            )
        } | \
        ItemTransformMixin._PROPERTIES_POS | \
        ItemTransformMixin._PROPERTIES_ROTATE

    # instance attributes
    _dot   : bool = False
    _clock : bool = False

    def dot(self : Self) -> bool:
        return self._dot

    def setDot(self : Self, value : bool) -> None:
        self._dot = value
        self._updateGraphics()

    def clock(self : Self) -> bool:
        return self._clock

    def setClock(self : Self, value : bool) -> None:
        self._clock = value
        self._updateGraphics()
        self._updateNameHandle()

    @withScene
    def _updateGraphics(self : Self, scene : "DrawingScene") -> None:
        key = (self._clock, self._dot)
        self.setPath(scene.resources.path(self.resourcesName(), key))

    def _updateNameHandle(self : Self | ItemHandlesMixin) -> None:
        """Allow for clock symbol."""
        settings_path = f"theme/items/{self.settingsName()}/pin"
        x = 0
        # allow for clock symbol
        if self._clock:
            x += settings().get(f"{settings_path}/clock/size")
        # allow for pen width
        x += settings().get(f"{settings_path}/wire/pen/width") / 2
        # standard offset
        x += WIDTH
        # apply to name handle
        name_handle = self.getHandle("Name")
        name_handle.setX(x)
