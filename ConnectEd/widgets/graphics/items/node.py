from typing import Self
from enum   import StrEnum
from math   import atan2, degrees

from PyQt6.QtCore    import QPointF, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsItem

from ....app import logger

from ....core.check import checked

from ..scenes import withScene

from .net_label import NetLabelItem

from .mixin              import ItemMixin
from .mixin.settings     import ItemSettingsMixin
from .mixin.presentation import ItemPresentationMixin
from .mixin.select       import ItemSelectMixin
from .mixin.change       import ItemChangeMixin
from .mixin.subscribe    import ItemSubscribeMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.diagram import DiagramScene
    from .segment  import SegmentItem


SCENE_POS_CHANGE = "scenePos"


class NodeState(StrEnum):
    UNCONNECTED = "unconnected"
    CONNECTED   = "connected"
    JUNCTION    = "junction"


class NodeItem(
    ItemMixin,
    ItemSettingsMixin,
    ItemPresentationMixin,
    ItemSelectMixin,
    ItemChangeMixin,
    ItemSubscribeMixin,
    QGraphicsPathItem
):
    _JUNCTION_THRESHOLD : int

    # instance attributes
    _state : NodeState

    @checked
    def __init__(self : Self, parent : QGraphicsItem | None = None) -> None:
        super().__init__(parent)
        self._state = NodeState.UNCONNECTED
        self.initItem()
        self.onSettingsChanged()

    def onScenePositionChanged(self : Self, _pos : QPointF) -> None:
        """Notify all scene-position subscribers."""
        self.callSubscribers(SCENE_POS_CHANGE)

    @withScene
    def onConnectionChanged(self : Self, scene : "DiagramScene | None" = None) -> None:
        n = self.degree()
        self._state = \
            NodeState.JUNCTION    if n >= self._JUNCTION_THRESHOLD else \
            NodeState.CONNECTED   if n >= 1 else \
            NodeState.UNCONNECTED
        self.onSceneChanged()  # update pen, brush and graphics

    def degree(self : Self) -> int:
        scene : "DiagramScene | None" = self.scene()
        if scene is None or not scene.netlist.hasNode(self):
            return 0
        return scene.netlist.nodeDegree(self)

    def segments(self : Self) -> list["SegmentItem"]:
        scene : "DiagramScene | None" = self.scene()
        if scene is None or not scene.netlist.hasNode(self):
            return []
        return scene.netlist.nodeSegments(self)

    @checked
    def toXml(self : Self, xw : QXmlStreamWriter, id : int) -> None:
        xw.writeStartElement(self.settingsName())
        xw.writeAttribute("ID", str(id))
        xw.writeAttribute("X", str(self.scenePos().x()))
        xw.writeAttribute("Y", str(self.scenePos().y()))
        xw.writeEndElement()

    @classmethod
    @checked
    def fromXml(cls : Self, xr : QXmlStreamReader) -> tuple[int, QPointF]:
        id  = -1
        pos = QPointF()
        for xml_attr in xr.attributes():
            match xml_attr.name():
                case "ID":
                    id = int(xml_attr.value())
                case "X":
                    pos.setX(float(xml_attr.value()))
                case "Y":
                    pos.setY(float(xml_attr.value()))
                case _:
                    logger().warning(
                        f"Unexpected attribute: "
                        f"{xml_attr.name()}={xml_attr.value()}"
                    )
        return id, pos

    def _penKey(self : Self) -> tuple[NodeState, bool]:
        return (self._state, self.isSelected())

    def _brushKey(self : Self) -> tuple[NodeState, bool]:
        return (self._state, self.isSelected())

    def _updateGraphics(self : Self, scene : "DiagramScene") -> None:
        self.setPath(scene.resources.path(self.resourcesName(), self._state))


class FreeNodeItem(NodeItem):
    _JUNCTION_THRESHOLD = 3

    @checked
    def __init__(
        self : Self,
        pos  : QPointF | None = None
    ) -> None:
        super().__init__()
        if pos is not None:
            self.setPos(pos)

    @classmethod
    @checked
    def fromXml(cls : Self, xr : QXmlStreamReader) -> tuple[int, Self]:
        id  = -1
        pos = QPointF()
        for xml_attr in xr.attributes():
            match xml_attr.name():
                case "ID":
                    id = int(xml_attr.value())
                case "X":
                    pos.setX(float(xml_attr.value()))
                case "Y":
                    pos.setY(float(xml_attr.value()))
                case _:
                    logger().warning(
                        f"Unexpected attribute: "
                        f"{xml_attr.name()}={xml_attr.value()}"
                    )
        return id, cls(pos)


class FixedNodeItem(NodeItem):
    _JUNCTION_THRESHOLD = 2

    @checked
    def onSelectionChanged(self : Self, selected : bool) -> None:
        super().onSelectionChanged(selected)
        parent = self.parentItem()
        if parent is not None:
            parent.setSelected(selected)

    @checked
    def sceneEscapeAngle(self : Self) -> float:
        """
        Scene angle (degrees) from pin origin towards tip.
        Allows for cumulative rotation and mirroring.
        """
        pin = self.parentItem()
        if pin is None:
            return 0.0
        local = self.pos()
        if local.x() == 0.0 and local.y() == 0.0:
            return 0.0
        escape = pin.mapToScene(local) - pin.mapToScene(QPointF())
        if escape.x() == 0.0 and escape.y() == 0.0:
            return 0.0
        return degrees(atan2(escape.y(), escape.x())) % 360.0


class TapMajorNodeItem(FixedNodeItem):
    pass


class TapMinorNodeItem(FixedNodeItem):
    pass


# Pin/tap attachment nodes used by diagram connectivity APIs (not free vertices).
PinNodeItem = FixedNodeItem
TapNodeItem = TapMajorNodeItem | TapMinorNodeItem
AttachedNodeItem = FixedNodeItem | TapMajorNodeItem | TapMinorNodeItem
