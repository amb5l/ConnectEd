from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsLineItem, QGraphicsItem
from ....core.defs   import WIDTH
from ....core.types  import Direction, DataKind

from ..properties import InherentProperty, PropertiesMixin

from ..scenes import withScene

from .node import FixedNodeItem

from .mixin         import ItemMixin
from .mixin.handle  import ItemHandlesMixin
from .mixin.paint   import ItemPaintMixin
from .mixin.line    import ItemLineMixin
from .mixin.change  import ItemChangeMixin
from .mixin.clone   import ItemCloneMixin
from .mixin.xml     import ItemXmlMixin
from .mixin.menu    import ItemMenuMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.drawing import DrawingScene


class PortPinMixin(
    ItemMixin,
    ItemLineMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemXmlMixin,
    ItemMenuMixin,
    PropertiesMixin
):
    # class attributes
    _PROPERTIES_NAME = \
        {
            "Name" : InherentProperty(
                kind   = DataKind.STR,
                getter = lambda self: self._name,
                setter = lambda self, value: setattr(self, "_name", value),
            )
        }
    _PROPERTIES_DIR = \
        {
            "Dir" : InherentProperty(
                kind   = DataKind.DIRECTION,
                getter = lambda self: self._direction,
                setter = lambda self, value: setattr(self, "_direction", value)
            )
        }
    _PROPERTIES_COMMENT = \
        {
            "Comment" : InherentProperty(
                kind   = DataKind.STR,
                worthy = lambda self: self._comment != "",
                getter = lambda self: self._comment,
                setter = lambda self, value: setattr(self, "_comment", value)
            )
        }
    _PEN_CAP_STYLE  = Qt.PenCapStyle.SquareCap
    _PEN_JOIN_STYLE = Qt.PenJoinStyle.MiterJoin

    # instance attributes
    _name      : str
    _direction : Direction
    _comment   : str
    _node      : FixedNodeItem

    def initPortPin(self : Self | QGraphicsPathItem, fresh : bool) -> None:
        # Initialize attributes that properties will access
        self._name      = ""
        self._direction = Direction.IN
        self._comment   = ""
        # Initialize the item (this sets up properties system)
        self.initItem(fresh)
        # Initialize the node
        self._node = FixedNodeItem(parent=self)

    def initHandles(self : Self) -> None:
        raise NotImplementedError("Subclass must implement this method")

    def name(self : Self) -> str:
        return self._name

    def setName(self : Self, value : str) -> None:
        self._name = value
        self.signalPropertyChanges("Name")

    def direction(self : Self) -> Direction:
        return self._direction

    def setDirection(self : Self, value : Direction) -> None:
        self._direction = value
        self.signalPropertyChanges("Dir")

    def comment(self : Self) -> str:
        return self._comment

    def setComment(self : Self, value : str) -> None:
        self._comment = value
        self.signalPropertyChanges("Comment")


class PortPinArrowItem(ItemPaintMixin, ItemChangeMixin, QGraphicsPathItem):
    def __init__(self : Self, parent : QGraphicsItem | None = None) -> None:
        super().__init__(parent)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

    def onSelectionChange(self : Self, selected : bool) -> None:
        parent = self.parentItem()
        if parent is not None:
            parent.setSelected(selected)


class PortPinItem(
    ItemMixin,
    ItemPaintMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemXmlMixin,
    ItemMenuMixin,
    PropertiesMixin,
    QGraphicsLineItem
):
    """
    Base class for ports and block/symbol pins.
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
        QGraphicsLineItem.__init__(self, parent)
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

    def onSettingsChange(self : Self) -> None:
        self.onSceneChange()

    @withScene
    def onSceneChange(self : Self, scene : "DrawingScene") -> None:
        self._updateLine(scene)
        self._updatePen(scene)
        self._updateArrowPath(scene)
        self._updateArrowPenBrush(scene)

    def onSelectionChange(self : Self, selected : bool) -> None:
        scene : "DrawingScene" = self.scene()
        self._updatePen(scene)
        self._updateArrowPenBrush(scene)
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

    def _updateLine(self : Self, scene : "DrawingScene") -> None:
        self.setLine(scene.rsrcman.line(self.__class__))

    def _updatePen(self : Self, scene : "DrawingScene") -> None:
        key = (self.bus(), self.isSelected())
        self.setPen(scene.rsrcman.pen(self.__class__, key))

    def _updateArrowPath(self : Self, scene : "DrawingScene") -> None:
        self._arrow.setPath(scene.rsrcman.path(self._ARROW_CLS, self._direction))

    def _updateArrowPenBrush(
        self  : Self | ItemHandlesMixin,
        scene : "DrawingScene"
    ) -> None:
        key = self.isSelected()
        self._arrow.setPen(scene.rsrcman.pen(self._ARROW_CLS, key))
        self._arrow.setBrush(scene.rsrcman.brush(self._ARROW_CLS, key))
        name_handle = self.getHandle("Name")
        x = self._arrow.pos().x() + self._arrow.boundingRect().right() + WIDTH
        name_handle.setX(x)
