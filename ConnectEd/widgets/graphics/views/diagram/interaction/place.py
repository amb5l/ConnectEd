from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtGui     import QAction
from PyQt6.QtWidgets import QMenu

from ......core.check import checked
from ......core.utils import sign

from ....items.port      import PortItem
from ....items.gate      import LogicGateItem
from ....items.block     import BlockItem
from ....items.block_pin import BlockPinItem
from ....items.node      import NodeItem
from ....items.segment   import SegmentItem, SegmentPreview1Item, SegmentPreview2Item
from ....items.tap       import TapItem

from ...drawing.interaction import Interaction, RotateItemMixin

from ...drawing.interaction.place import PlaceBase1PosInteraction, \
                                         PlaceBase2PosInteraction

from . import BlockPinInteraction

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DiagramView
    from ....scenes.diagram import DiagramScene

class PlacePortInteraction(RotateItemMixin, PlaceBase1PosInteraction):
    _ITEM_TYPE = PortItem


class PlaceGateInteraction(RotateItemMixin, PlaceBase1PosInteraction):
    _ITEM_TYPE = LogicGateItem


class PlaceBlockInteraction(PlaceBase2PosInteraction):
    _ITEM_TYPE = BlockItem


class PlaceBlockPinInteraction(BlockPinInteraction):
    @checked
    def __init__(
        self   : Self,
        view   : "DiagramView",
        parent : BlockItem,
        pin    : BlockPinItem,
        pos    : QPointF,
        snap   : QPointF | None = None
    ) -> None:
        super().__init__(view, parent, pin, pos, snap)

    def update(self : Self, pos : QPointF, snap : QPointF | None = None) -> None:
        self._pin.setLoc(self._pin.locSnap(self._parent.pos2loc(pos), snap))

    def _commit(self : Self, pos : QPointF, snap : QPointF | None = None) -> bool:
        self.update(pos, snap)
        self._scene.addBlockPin(self._parent, self._pin, undoable=True)
        return True

    def _cancel(self : Self) -> None:
        self._pin.setParentItem(None)


class PlaceConnInteraction(Interaction):
    """Interactive wire placement involves two preview segments."""

    # instance attributes
    _scene : "DiagramScene"
    _seg1  : SegmentPreview1Item
    _seg2  : SegmentPreview2Item

    @checked
    def __init__(
        self : Self,
        view : "DiagramView",
        pos  : QPointF
    ) -> None:
        super().__init__(view)
        self._seg1 = SegmentPreview1Item()
        self._seg2 = SegmentPreview2Item()
        self._setP0(pos)
        self._setP1(pos)
        self._setP2(pos)
        self._scene.addItem(self._seg1)
        self._scene.addItem(self._seg2)

    def valid(self : Self) -> bool:
        return True

    def update(self : Self, pos : QPointF) -> None:
        self._updateVertices(pos)

    def _commit(self : Self, pos : QPointF, complete : bool = False) -> bool:
        self._updateVertices(pos)
        # probe for terminals at both preview segment endpoints before changes
        terminals_1 = [
            i for i in self._scene.items(self._p1()) \
                if isinstance(i, SegmentItem | NodeItem)
        ]
        terminals_2 = [
            i for i in self._scene.items(self._p2()) \
                if isinstance(i, SegmentItem | NodeItem)
        ]
        # create first segment
        self._scene.addSegment(self._p0(), self._p1(), undoable=True)
        completed = False
        if terminals_1:
            # terminal reached at end of first preview segment
            self._cleanup()
        elif complete or terminals_2:
            # complete or terminal reached at end of second preview segment
            self._scene.addSegment(self._p1(), self._p2(), undoable=True)
            self._cleanup()
        else:
            # continue interaction
            self._restart(pos)
            completed = False
        self._scene.netlistChanged.emit()
        return completed

    def _complete(self : Self, pos : QPointF) -> None:
        self.commit(pos, complete=True)

    def _cancel(self : Self) -> None:
        self._cleanup()

    def _p0(self : Self) -> QPointF:
        return self._seg1.p1()

    def _setP0(self : Self, pos : QPointF) -> None:
        self._seg1.setP1(pos)

    def _p1(self : Self) -> QPointF:
        return self._seg1.p2()

    def _setP1(self : Self, pos : QPointF) -> None:
        self._seg1.setP2(pos)
        self._seg2.setP1(pos)

    def _p2(self : Self) -> QPointF:
        return self._seg2.p2()

    def _setP2(self : Self, pos : QPointF) -> None:
        self._seg2.setP2(pos)

    def _updateVertices(self : Self, pos : QPointF) -> None:
        v0 = self._seg1.p1()
        v1 = self._seg1.p2()
        # update end point
        self._seg2.setP2(pos)
        # conditions
        h = v1.y() == v0.y()
        v = v1.x() == v0.x()
        h_restart = h and sign(pos.x() - v0.x()) != sign(v1.x() - v0.x())
        v_restart = v and sign(pos.y() - v0.y()) != sign(v1.y() - v0.y())
        # if new start or restart, establish first segment based on quadrant
        if v1 == v0 or h_restart or v_restart:
            vector = pos - v0
            if abs(vector.x()) >= abs(vector.y()):
                self._setP1(QPointF(pos.x(), v0.y()))
            else:
                self._setP1(QPointF(v0.x(), pos.y()))
        # update first segment
        elif h and not v:
            self._setP1(QPointF(pos.x(), v0.y()))
        elif v and not h:
            self._setP1(QPointF(v0.x(), pos.y()))
        else:
            self._setP1(pos)

    def _restart(self : Self, pos : QPointF) -> None:
        self._setP0(self._p1())
        self._updateVertices(pos)

    def _cleanup(self : Self) -> None:
        for item in [self._seg1, self._seg2]:
            if item.scene() is not None:
                item.scene().removeItem(item)


class PlaceTapInteraction(PlaceBase1PosInteraction):
    _ITEM_TYPE = TapItem

    _item : TapItem

    def rotateCW(self : Self) -> None:
        self._item.reorientCW()

    def rotateCCW(self : Self) -> None:
        self._item.reorientCCW()

    def ctxMenuItems(self : Self, pos : QPointF) -> list[QAction | QMenu]:
        return super().ctxMenuItems(pos) + [
            self._view.separator(),
            self._view.action("Rotate CW", self.rotateCW, "]"),
            self._view.action("Rotate CCW", self.rotateCCW, "["),
        ]
