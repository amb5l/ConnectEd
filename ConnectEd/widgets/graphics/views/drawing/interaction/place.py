from typing import Self

from PyQt6.QtCore    import Qt, QPointF
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui     import QAction

from ......core.check import checked

from .....dialogs.arc import ArcDialog

from ....items import ItemType

from ....items.symbol_pin import SymbolPinItem
from ....items.line       import LineItem
from ....items.rectangle  import RectangleItem
from ....items.ellipse    import EllipseItem
from ....items.polyline   import PolylineItem
from ....items.text       import TextItem

from . import DrawingItemInteraction

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingView


class DrawingPlaceBaseInteraction(DrawingItemInteraction):  # _view, _scene, _item, valid
    """Base for all interactions that place a single item."""

    # class attributes
    _ITEM_TYPE : ItemType  # subclass to override with item class

    # instance attributes
    _pos : QPointF | None

    @checked
    def __init__(
        self : Self,
        view : "DrawingView",
        pos  : QPointF,
        item : ItemType | None = None
    ) -> None:
        if item is None:
            item = self._ITEM_TYPE(pos)
        else:
            item.setPos(pos)
        super().__init__(view, item)
        if self._item.scene() != self._scene:
            self._scene.addItem(self._item)
        self._item.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self._item.setSelected(True)
        self._pos = None

    def _cancel(self : Self) -> None:
        self._scene.removeItem(self._item)


class DrawingPlaceBase1PosInteraction(DrawingPlaceBaseInteraction):
    """Base for all interactions that place a single item using 1 position."""

    def update(self : Self, pos : QPointF) -> None:
        if pos == self._pos:
            return  # filter redundant updates
        self._pos = pos
        self._item.setPos(pos)

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


class DrawingPlaceBase2PosInteraction(DrawingPlaceBase1PosInteraction):
    """Base for all interactions that place a single item using 2 positions."""

    # instance attributes
    _item : ItemType  # type hint for this interaction
    _p1   : QPointF   # first position

    @checked
    def __init__(
        self : Self,
        view : "DrawingView",
        pos  : QPointF,
        item : ItemType | None = None
    ) -> None:
        super().__init__(view, pos, item)
        self._p1 = pos

    def update(self : Self, pos : QPointF) -> None:
        if pos == self._pos:
            return  # filter redundant updates
        self._pos = pos
        self._item.setPoints(self._p1, pos)


class DrawingPlaceSymbolPinInteraction(DrawingPlaceBase1PosInteraction):
    _ITEM_TYPE = SymbolPinItem


class DrawingPlaceLineInteraction(DrawingPlaceBase2PosInteraction):
    _ITEM_TYPE = LineItem


class DrawingPlaceRectangleInteraction(DrawingPlaceBase2PosInteraction):
    _ITEM_TYPE = RectangleItem


class DrawingPlaceEllipseInteraction(DrawingPlaceBase2PosInteraction):
    _ITEM_TYPE = EllipseItem


class DrawingPlacePolylineInteraction(DrawingPlaceBase1PosInteraction):
    _ITEM_TYPE = PolylineItem

    _item  : PolylineItem      # type hint for this interaction
    _sweep : float | None  # sweep angle for last segment

    @checked
    def __init__(
        self : Self,
        view : "DrawingView",
        pos  : QPointF,
        item : PolylineItem | None = None
    ) -> None:
        super().__init__(view, pos, item)
        self._item.addVertex(pos)  # WIP polyline now has 2 vertices
        self._item.setSelMode(1)
        self._sweep = None

    def update(self : Self, pos : QPointF) -> None:
        if pos == self._pos:
            return  # filter redundant updates
        self._pos = pos
        self._item.setLastVertexPos(pos)  # local coordinates

    def _commit(self : Self, pos : QPointF) -> bool:
        # Ensure last vertex is at the click position
        self.update(pos)
        # Only proceed if the last vertex has moved from the previous one
        if self._item.vertex(-1).pos() == self._item.vertex(-2).pos():
            return False  # continue interaction
        if self._item.vertexCount() == 2:
            # Add polyline to scene when 2nd vertex is committed
            sel_mode = self._item.selMode()  # Save selection mode
            self._scene.addItems([self._item], undoable=True)
            self._item.setSelMode(sel_mode)  # Restore selection mode
            self._item.addVertex(pos)  # add WIP vertex
            self._sweep = None
            return False  # continue interaction
        # Handle closing the polyline
        if pos == self._item.pos():
            self._item.delLastVertex()  # remove WIP vertex
            self._scene.editPolylineClosed(self._item, True, self._sweep, undoable=True)
            return True  # interaction completed
        # Add vertex to polyline when 3rd+ vertex is committed
        self._item.delLastVertex()  # remove WIP vertex
        self._scene.addPolyVtx(self._item, pos, self._sweep, undoable=True)
        self._item.addVertex(pos)  # add WIP vertex
        self._sweep = None
        return False  # continue interaction

    def _complete(self : Self, pos : QPointF) -> None:
        if not self.commit(pos):
            self._item.delLastVertex()  # remove WIP vertex

    def _cancel(self : Self) -> None:
        """Escape works a bit differently here."""
        self._item.delLastVertex()  # remove WIP vertex

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


class DrawingPlaceTextInteraction(DrawingPlaceBase1PosInteraction):
    _ITEM_TYPE = TextItem
