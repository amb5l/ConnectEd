from typing import Self

from PyQt6.QtCore    import QPointF, QLineF
from PyQt6.QtGui     import QAction
from PyQt6.QtWidgets import QGraphicsLineItem, QMenu

from ....core.defs  import PITCH
from ....core.types import NetKind, DataKind, AlignH, AlignV, \
                           RectHandleId, TapHandleId
from ....core.check import checked

from ..properties import PropertiesMixin, InherentProperty, PropertyTextSpec

from .node   import TapMajorNodeItem, TapMinorNodeItem
from .handle import HandleItem
from .grip   import MoveGripItem

from .mixin import ItemMixin

from .mixin.transform import ItemTransformMixin
from .mixin.paint     import ItemPaintMixin
from .mixin.handle    import ItemHandlesMixin
from .mixin.change    import ItemChangeMixin
from .mixin.xml       import ItemXmlMixin
from .mixin.menu      import ItemMenuMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.diagram  import DiagramView
    from ..scenes.diagram import DiagramScene


class TapItem(
    ItemMixin,
    ItemTransformMixin,
    ItemPaintMixin,
    ItemHandlesMixin[TapHandleId],
    ItemChangeMixin,
    ItemXmlMixin,
    ItemMenuMixin,
    PropertiesMixin,
    QGraphicsLineItem
):
    # class attributes
    _LINE = QLineF(0, 0, PITCH, PITCH)
    _PROPERTIES = \
        {
            "Suffix" : InherentProperty(
                kind   = DataKind.STR,
                worthy = lambda self: self.suffix() != "",
                getter = lambda self: self.suffix(),
                setter = lambda self, value: self.setSuffix(value)
            )
        } | \
        ItemTransformMixin._PROPERTIES_POS | \
        ItemTransformMixin._PROPERTIES_ROTATE | \
        ItemTransformMixin._PROPERTIES_MIRROR
    _PROPERTY_TEXTS = {
        "Suffix" : PropertyTextSpec(
            cleat=TapHandleId.SUFFIX, origin=RectHandleId.MIDDLE_LEFT
        )
    }

    @classmethod
    def handleIdType(cls) -> type[TapHandleId]:
        return TapHandleId

    @classmethod
    def handleIdKind(cls) -> DataKind:
        return DataKind.TAP_HANDLE

    # instance attributes
    _line        : QLineF
    _major_node  : TapMajorNodeItem
    _minor_node  : TapMinorNodeItem
    _net_kind    : NetKind
    _index_width : float
    _range_width : float


    @checked
    def __init__(
        self  : Self,
        pos   : QPointF,
        fresh : bool = True
    ) -> None:
        QGraphicsLineItem.__init__(self)
        self.setPos(pos)
        self.setLine(self._LINE)
        self.initItem(fresh)
        self._major_node = TapMajorNodeItem(self)
        self._major_node.setPos(0, 0)
        self._minor_node = TapMinorNodeItem(self)
        self._minor_node.setPos(PITCH, PITCH)
        self._net_kind = NetKind.UNRESOLVED
        self._index_width = 15.0  # default fixed width
        self._range_width = -1.0  # auto width

    @checked
    def onSettingsChanged(self : Self) -> None:
        if (scene := self.scene()) is not None:
            self.onSceneChanged(scene)

    @checked
    def onSceneChanged(self : Self, scene : "DiagramScene | None") -> None:
        if scene is None:
            return
        self.setPen(scene.resources.pen(
            "Tap", (self._net_kind, self.isSelected()))
        )

    @checked
    def onConnectivityChanged(self : Self) -> None:
        # update self._state based on self._node1 and self._node2
        pass

    @checked
    def initHandles(self : Self) -> None:
        self._handles = {
            TapHandleId.SUFFIX : HandleItem(
                id       = TapHandleId.SUFFIX,
                pos      = QPointF(0, 5),
                grip_cls = MoveGripItem,
                parent   = self
            )
        }

    def moveHandleBy(self : Self, _, d : QPointF) -> None:
        self.setPos(self.pos() + d)

    @checked
    def majorNode(self : Self) -> TapMajorNodeItem:
        return self._major_node

    @checked
    def minorNode(self : Self) -> TapMinorNodeItem:
        return self._minor_node

    @checked
    def suffix(self : Self) -> str:
        return self._suffix

    @checked
    def setSuffix(self : Self | PropertiesMixin, suffix : str) -> None:
        self._suffix = suffix
        pt = self.properties.text("Suffix")
        if pt is not None:
            if ":" in suffix:
                # range
                pt.setOrigin(RectHandleId.MIDDLE_LEFT)
                pt.setWidth(-1.0)  # auto width
                pt.setAlignH(AlignH.LEFT)
                pt.setAlignV(AlignV.MIDDLE)
            else:
                # index
                pt.setOrigin(RectHandleId.MIDDLE_RIGHT)
                pt.setWidth(-1.0)  # auto width
                pt.setAlignH(AlignH.RIGHT)
                pt.setAlignV(AlignV.MIDDLE)
        self.properties.signalChanges("Suffix")


    @checked
    def ctxMenuItems(self : Self, view : "DiagramView", _spos : QPointF) -> list[QAction | QMenu]:
        return [
            view.action("Rotate CW",  lambda: self.rotateCW(),  shortcut="]"),
            view.action("Rotate CCW", lambda: self.rotateCCW(), shortcut="["),
        ]
