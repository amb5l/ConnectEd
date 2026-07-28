from __future__ import annotations

from typing import Self, TypeVar

from PyQt6.QtCore    import Qt, QPointF
from PyQt6.QtWidgets import QGraphicsItem, QMenu
from PyQt6.QtGui     import QAction

from ......core.check import checked
from ......core.types import EdgeLoc
from ......core.utils import sign

from .....dialogs.arc import ArcDialog

from ....items.line       import LineItem
from ....items.rectangle  import RectangleItem
from ....items.ellipse    import EllipseItem
from ....items.polyline   import PolylineItem
from ....items.text       import TextItem
from ....items.port       import PortItem
from ....items.gate       import LogicGateItem
from ....items.block      import BlockItem
from ....items.block_pin  import BlockPinItem
from ....items.symbol_pin import SymbolPinItem
from ....items.node       import NodeItem
from ....items.segment    import SegmentItem, SegmentPreview1Item, SegmentPreview2Item
from ....items.tap        import TapItem
from ....items.net_label  import NetLabelItem

from ....items.protocols import SetPointsProtocol

from . import (
    DiagramInteraction,
    DiagramItemInteraction,
    DiagramBlockPinInteraction,
    RotateItemMixin
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DiagramView


TItem = TypeVar("TItem", bound=QGraphicsItem)


class DiagramPlaceBaseInteraction(DiagramItemInteraction[TItem]):  # _view, _scene, _item, valid
    """Base for all interactions that place a single item."""

    # class attributes
    _ITEM_TYPE : type[TItem]  # subclass to override with item class
    _item : TItem

    # instance attributes
    _pos : QPointF | None

    @checked
    def __init__(
        self : Self,
        view : DiagramView,
        pos  : QPointF,
        item : TItem | None = None
    ) -> None:
        if item is None:
            item = self._ITEM_TYPE()
        item.setPos(pos)
        super().__init__(view, item)
        if self._item.scene() != self._scene:
            self._scene.addItem(self._item)
        self._item.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self._item.setSelected(True)
        self._pos = None

    def _cancel(self : Self) -> None:
        self._scene.removeItem(self._item)


class DiagramPlaceBase1PosInteraction(DiagramPlaceBaseInteraction[TItem]):
    """Base for all interactions that place a single item using 1 position."""

    def update(self : Self, pos : QPointF) -> None:
        if pos == self._pos:
            return  # filter redundant updates
        self._pos = pos
        self._item.setPos(pos)

    @checked
    def _commit(self : Self, pos : QPointF) -> bool:
        self.update(pos)
        self._item.setAcceptedMouseButtons(Qt.MouseButton.AllButtons)
        self._scene.addItems([self._item], undoable=True)
        return True

    def _complete(self : Self, pos : QPointF) -> None:
        self.commit(pos)

    def _finish(self : Self, pos : QPointF) -> None:
        if self.commit(pos):
            self._view.state.go(self._view.stateIdle)

    def ctxMenuItems(self : Self, pos : QPointF) -> list[QAction | QMenu]:
        pos = self._view._snap(pos)
        return [
            self._view.action("Finish", lambda: self._finish(pos)),
        ] + super().ctxMenuItems(pos)


class DiagramPlaceBase2PosInteraction(DiagramPlaceBase1PosInteraction[TItem]):
    """Base for all interactions that place a single item using 2 positions."""

    # instance attributes
    _p1 : QPointF  # first position

    @checked
    def __init__(
        self : Self,
        view : DiagramView,
        pos  : QPointF,
        item : TItem | None = None
    ) -> None:
        super().__init__(view, pos, item)
        self._p1 = pos

    def update(self : Self, pos : QPointF) -> None:
        if pos == self._pos:
            return  # filter redundant updates
        self._pos = pos
        if isinstance(item := self._item, SetPointsProtocol):
            item.setPoints(self._p1, pos)


class DiagramPlaceLineInteraction(DiagramPlaceBase2PosInteraction):
    _ITEM_TYPE = LineItem


class DiagramPlaceRectangleInteraction(DiagramPlaceBase2PosInteraction):
    _ITEM_TYPE = RectangleItem


class DiagramPlaceEllipseInteraction(DiagramPlaceBase2PosInteraction):
    _ITEM_TYPE = EllipseItem


class DiagramPlacePolylineInteraction(DiagramPlaceBase1PosInteraction):
    _ITEM_TYPE = PolylineItem

    _item  : PolylineItem      # type hint for this interaction
    _sweep : float | None  # sweep angle for last segment

    @checked
    def __init__(
        self : Self,
        view : DiagramView,
        pos  : QPointF,
        item : PolylineItem | None = None
    ) -> None:
        super().__init__(view, pos, item)
        self._item.addVertex(pos)  # WIP polyline now has 2 vertices
        self._item.setSelectMode(1)
        self._sweep = None

    def update(self : Self, pos : QPointF) -> None:
        if pos == self._pos:
            return  # filter redundant updates
        self._pos = pos
        self._item.setLastVertexPos(pos)  # local coordinates

    def _releaseItem(self : Self) -> None:
        self._item.setAcceptedMouseButtons(Qt.MouseButton.AllButtons)

    def _complete(self : Self, pos : QPointF) -> None:
        if not self.commit(pos):
            self._item.delLastVertex()  # remove WIP vertex
        self._releaseItem()

    @checked
    def _commit(self : Self, pos : QPointF) -> bool:
        # Ensure last vertex is at the click position
        self.update(pos)
        # Only proceed if the last vertex has moved from the previous one
        if self._item.vertex(-1).pos() == self._item.vertex(-2).pos():
            return False  # continue interaction
        if self._item.vertexCount() == 2:
            # Add polyline to scene when 2nd vertex is committed
            sel_mode = self._item.selectMode()  # Save selection mode
            self._scene.addItems([self._item], undoable=True)
            self._item.setSelectMode(sel_mode)  # Restore selection mode
            self._item.addVertex(pos)  # add WIP vertex
            self._sweep = None
            return False  # continue interaction
        # Handle closing the polyline
        if pos == self._item.pos():
            self._item.delLastVertex()  # remove WIP vertex
            self._scene.editPolylineClosed(self._item, True, self._sweep, undoable=True)
            self._releaseItem()
            return True  # interaction completed
        # Add vertex to polyline when 3rd+ vertex is committed
        self._item.delLastVertex()  # remove WIP vertex
        self._scene.addPolyVtx(self._item, pos, self._sweep, undoable=True)
        self._item.addVertex(pos)  # add WIP vertex
        self._sweep = None
        return False  # continue interaction

    def _cancel(self : Self) -> None:
        """Escape works a bit differently here."""
        self._item.delLastVertex()  # remove WIP vertex
        if self._item.scene() is not None:
            self._releaseItem()

    def ctxMenuItems(self : Self, pos : QPointF) -> list[QAction | QMenu]:
        pos = self._view._snap(pos)
        items = []
        items.append(self._view.action("Continue", lambda: self.commit(pos)))
        items.append(self._view.action("Finish", lambda: self._finish(pos)))
        items.extend(super().ctxMenuItems(pos))
        items.append(self._view.separator())
        a = self._item.lastSegment().sweep()
        items.append(self._view.action("Line", self._toLine, a is None))
        a_text = f" ({a}°)" if a is not None else ""
        items.append(self._view.action(f"Arc{a_text}...", self._toArc, a is not None))
        items.append(self._view.separator())
        items.append(self._view.action("Closed", self._toggleClosed, self._item.closed()))
        return items

    def _finish(self : Self, pos : QPointF) -> None:
        self.complete(pos)
        self._view.state.go(self._view.stateIdle)

    def _toggleClosed(self : Self) -> None:
        self._item.setClosed(not self._item.closed())

    def _toLine(self : Self) -> None:
        self._sweep = None
        self._item.lastSegment().setSweep(self._sweep)

    def _toArc(self : Self) -> None:
        dialog = ArcDialog(self._item.lastSegment().sweep(), self._view)
        if dialog.exec():
            self._sweep = dialog.getAngle()
            self._item.lastSegment().setSweep(self._sweep)


class DiagramPlaceTextInteraction(DiagramPlaceBase1PosInteraction[TextItem]):
    pass


class DiagramPlacePortInteraction(
    RotateItemMixin, DiagramPlaceBase1PosInteraction[PortItem]
):
    pass


class DiagramPlaceGateInteraction(
    RotateItemMixin, DiagramPlaceBase1PosInteraction
):
    _ITEM_TYPE = LogicGateItem


class DiagramPlaceBlockInteraction(DiagramPlaceBase2PosInteraction):
    _ITEM_TYPE = BlockItem


class DiagramPlaceBlockPinInteraction(DiagramBlockPinInteraction):
    # instance attributes
    _loc : EdgeLoc | None

    @checked
    def __init__(
        self   : Self,
        view   : DiagramView,
        parent : BlockItem,
        pin    : BlockPinItem,
        pos    : QPointF,
        snap   : QPointF | None = None
    ) -> None:
        self._loc = None
        super().__init__(view, parent, pin, pos, snap)

    def update(self : Self, pos : QPointF, snap : QPointF | None = None) -> None:
        loc = self._pin.locSnap(self._parent.pos2loc(pos), snap)
        if loc == self._loc:
            return  # filter redundant updates
        self._loc = loc
        self._pin.setLoc(loc)

    @checked
    def _commit(self : Self, pos : QPointF, snap : QPointF | None = None) -> bool:
        self.update(pos, snap)
        self._scene.addBlockPin(self._parent, self._pin, undoable=True)
        return True

    def _cancel(self : Self) -> None:
        self._pin.setParentItem(None)


class DiagramPlaceSymbolPinInteraction(DiagramPlaceBase1PosInteraction):
    _ITEM_TYPE = SymbolPinItem


class DiagramPlaceConnInteraction(DiagramInteraction):
    """Interactive wire placement involves two preview segments."""

    # instance attributes
    _seg1  : SegmentPreview1Item
    _seg2  : SegmentPreview2Item
    _pos   : QPointF

    @checked
    def __init__(
        self : Self,
        view : DiagramView,
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
        self._pos = pos

    def valid(self : Self) -> bool:
        return True

    def update(self : Self, pos : QPointF) -> None:
        if pos == self._pos:
            return  # filter redundant updates
        self._pos = pos
        self._updateVertices(pos)

    @checked
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


class DiagramPlaceTapInteraction(DiagramPlaceBase1PosInteraction):
    _ITEM_TYPE = TapItem

    _item : TapItem

    def rotateCW(self : Self) -> None:
        raise NotImplementedError("Not implemented")
        #self._item.reorientCW()

    def rotateCCW(self : Self) -> None:
        raise NotImplementedError("Not implemented")
        #self._item.reorientCCW()

    def ctxMenuItems(self : Self, pos : QPointF) -> list[QAction | QMenu]:
        return [
            self._view.action("Rotate CW",  self.rotateCW,  shortcut="]"),
            self._view.action("Rotate CCW", self.rotateCCW, shortcut="["),
            self._view.separator()
        ] + super().ctxMenuItems(pos)


class DiagramPlaceNetLabelInteraction(DiagramPlaceBase1PosInteraction):
    _ITEM_TYPE = NetLabelItem
