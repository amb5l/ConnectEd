from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui     import QAction

from ......core.utils import sign

from .....dialogs.arc import ArcDialog

from ....items.block      import Block
from ....items.port       import Port
from ....items.block_pin  import BlockPin
from ....items.symbol_pin import SymbolPin
from ....items.entry      import Entry
from ....items.conn_vtx   import ConnVtx
from ....items.conn_seg   import ConnSeg, ConnSegPreview1, ConnSegPreview2
from ....items.line       import Line
from ....items.rectangle  import Rectangle
from ....items.ellipse    import Ellipse
from ....items.polyline   import Polyline
from ....items.text       import Text
from ....items.text_block import TextBlock

from ....scenes.drawing.cmd import CmdAdd, CmdAddBlockPin

from . import Interaction,         \
              SelectionMixin,      \
              RotateItemMixin,     \
              ItemInteraction,     \
              BlockPinInteraction, \
              ItemType

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingView


class PlaceBaseInteraction(
    SelectionMixin,  # _preserveSelection, _restoreSelection
    ItemInteraction  # _view, _scene, _item, valid
):
    """Base for all interactions that place a single item."""

    # class attributes
    _ITEM : ItemType  # subclass to override with item class

    def __init__(
        self : Self,
        view : "DrawingView",
        pos  : QPointF,
        item : ItemType | None = None
    ) -> None:
        if item is None:
            item = self._ITEM(pos)
        else:
            item.setPos(pos)
        super().__init__(view, item)
        self._preserveSelection()
        self._scene.clearSelection()
        self._scene.addItem(self._item)
        self._item.setSelected(True)

    def cancel(self : Self) -> None:
        self._scene.removeItem(self._item)
        self._restoreSelection()


class PlaceBase1PosInteraction(PlaceBaseInteraction):
    """Base for all interactions that place a single item using 1 position."""

    def update(self : Self, pos : QPointF):
        self._item.setPos(pos)

    def commit(self : Self, pos : QPointF) -> bool:
        self.update(pos)
        self._scene.undo_stack.push(CmdAdd(
            self._scene, [self._item], self._selection
        ))
        return True

    def complete(self : Self, pos : QPointF) -> None:
        self.commit(pos)

    def ctxMenuItems(self : Self, pos : QPointF) -> list[QAction | QMenu]:
        complete_action = QAction("Complete")
        complete_action.triggered.connect(lambda: self.commit(pos))
        cancel_action = QAction("Cancel")
        cancel_action.triggered.connect(self.cancel)
        return [complete_action, cancel_action]


class PlaceBase2PosInteraction(PlaceBase1PosInteraction):
    """Base for all interactions that place a single item using 2 positions."""

    # instance attributes
    _item : ItemType  # type hint for this interaction
    _p1   : QPointF   # first position

    def __init__(
        self : Self,
        view : "DrawingView",
        pos  : QPointF,
        item : ItemType | None = None
    ) -> None:
        super().__init__(view, pos, item)
        self._p1 = pos

    def update(self : Self, pos : QPointF):
        self._item.setPoints(self._p1, pos)


class PlacePortInteraction(RotateItemMixin, PlaceBase1PosInteraction):
    _ITEM = Port

    def ctxMenuItems(self : Self, pos : QPointF) -> list[QAction | QMenu]:
        separator = QAction()
        separator.setSeparator(True)
        rotate_cw_action = QAction("Rotate CW")
        rotate_cw_action.setShortcut("]")
        rotate_cw_action.triggered.connect(self.rotateCW)
        rotate_ccw_action = QAction("Rotate CCW")
        rotate_ccw_action.setShortcut("[")
        rotate_ccw_action.triggered.connect(self.rotateCCW)
        return super().ctxMenuItems(pos) + [
            separator,
            rotate_cw_action,
            rotate_ccw_action
        ]


class PlaceBlockInteraction(PlaceBase2PosInteraction):
    _ITEM = Block


class PlaceBlockPinInteraction(BlockPinInteraction):
    def __init__(
        self   : Self,
        view   : "DrawingView",
        parent : Block,
        pin    : BlockPin,
        pos    : QPointF,
        snap   : QPointF | None = None
    ) -> None:
        super().__init__(view, parent, pin, pos, snap)

    def update(self : Self, pos : QPointF, snap : QPointF | None = None) -> None:
        self._pin.setLoc(self._pin.locSnap(self._parent.pos2loc(pos), snap))

    def commit(self : Self, pos : QPointF, snap : QPointF | None = None) -> bool:
        self.update(pos, snap)
        self._scene.undo_stack.push(CmdAddBlockPin(self._parent, self._pin))
        return True

    def cancel(self : Self) -> None:
        self._pin.setParentItem(None)


class PlaceSymbolPinInteraction(PlaceBase1PosInteraction):
    _ITEM = SymbolPin


class PlaceLineInteraction(PlaceBase2PosInteraction):
    _ITEM = Line


class PlaceRectangleInteraction(PlaceBase2PosInteraction):
    _ITEM = Rectangle


class PlaceEllipseInteraction(PlaceBase2PosInteraction):
    _ITEM = Ellipse


class PlacePolylineInteraction(PlaceBase1PosInteraction):
    _ITEM = Polyline

    _item : Polyline  # type hint for this interaction

    def __init__(
        self : Self,
        view : "DrawingView",
        pos  : QPointF,
        item : ItemType | None = None
    ) -> None:
        super().__init__(view, pos, item)
        self._item.setSelMode(1)

    def update(self : Self, pos : QPointF):
        self._item.setLastVertexPos(pos-self._item.pos())  # local coordinates

    def commit(self : Self, pos : QPointF) -> bool:
        self._item.addVertex(pos-self._item.pos())  # local coordinates
        return False  # continue interaction

    def complete(self : Self, pos : QPointF) -> None:
        self.commit(pos)

    def ctxMenuItems(self : Self, pos : QPointF) -> list[QAction | QMenu]:
        items = []
        items.append(self._view.action("Add Point", lambda: self.commit(pos)))
        if self._item.vertexCount() > 2:
            items.append(self._view.action("Remove Point", self._item.removeLastVertex))
        s = "Make " + ("Open" if self._item.closed() else "Closed")
        items.append(self._view.action(
            s, lambda: self._item.setClosed(not self._item.closed())
        ))
        angle = self._item.lastSegment().sweep()
        items.append(self._view.action("Line", self._toLine, angle == 0))
        angle_text = f" ({angle}°)" if angle != 0 else ""
        items.append(self._view.action(f"Arc{angle_text}...", self._toArc, angle != 0))
        items.append(self._view.action("Closed", self._toggleClosed, self._item.closed()))
        return items

    def _toggleClosed(self : Self) -> None:
        self._item.setClosed(not self._item.closed())

    def _toLine(self : Self) -> None:
        self._item.lastSegment().setSweep(0)

    def _toArc(self : Self) -> None:
        dialog = ArcDialog(self._item.lastSegment().sweep(), self._view)
        if dialog.exec():
            self._item.lastSegment().setSweep(dialog.getAngle())


class PlaceTextInteraction(PlaceBase1PosInteraction):
    _ITEM = Text


class PlaceTextBlockInteraction(PlaceBase1PosInteraction):
    _ITEM = TextBlock


class PlaceConnInteraction(SelectionMixin, Interaction):
    """Interactive wire placement involves two preview segments."""

    # instance attributes
    _seg1  : ConnSegPreview1
    _seg2  : ConnSegPreview2

    def __init__(
        self : Self,
        view : "DrawingView",
        pos  : QPointF
    ) -> None:
        super().__init__(view)
        self._seg1 = ConnSegPreview1()
        self._seg2 = ConnSegPreview2()
        self._setP0(pos)
        self._setP1(pos)
        self._setP2(pos)
        self._scene.addItem(self._seg1)
        self._scene.addItem(self._seg2)
        self._preserveSelection()  # store prior selection set
        self._scene.clearSelection()

    def valid(self : Self) -> bool:
        return True

    def update(self : Self, pos : QPointF) -> None:
        self._updateVertices(pos)

    def commit(self : Self, pos : QPointF, complete : bool = False) -> bool:
        self._updateVertices(pos)
        # get scene content before changing it
        items_1 = self._scene.items(self._p1())
        connectables_1 = [item for item in items_1 \
            if isinstance(item, ConnSeg | ConnVtx | Entry)]
        items_2 = self._scene.items(self._p2())
        connectables_2 = [item for item in items_2 \
            if isinstance(item, ConnSeg | ConnVtx | Entry)]
        # create first segment
        self._scene.addConnSeg(self._p0(), self._p1(), undo=True)
        if connectables_1:
            self._cleanup()
            return True  # interaction completed
        # create second segment if...
        # - complete is requested
        # - mouse is over a connectable destination
        if complete or connectables_2:
            self._scene.addConnSeg(self._p1(), self._p2(), undo=True)
            self._cleanup()
            return True  # interaction completed
        self._restart(pos)
        return False  # continue interaction

    def complete(self : Self, pos : QPointF) -> None:
        self.commit(pos, complete=True)

    def cancel(self : Self) -> None:
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
            self._scene.removeItem(item)
