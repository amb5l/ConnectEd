from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui     import QAction

from ......core.utils import sign

from ....items.line       import Line
from ....items.base_rect  import BaseRectangle
from ....items.block      import Block
from ....items.rectangle  import Rectangle
from ....items.text       import Text
from ....items.text_block import TextBlock
from ....items.port       import Port
from ....items.block_pin  import BlockPin
from ....items.symbol_pin import SymbolPin
from ....items.entry      import Entry
from ....items.conn_vtx   import ConnVtx
from ....items.conn_seg   import ConnSeg, ConnSegPreview1, ConnSegPreview2

from ....scenes.drawing.cmd import cmdAdd, cmdAddBlockPin

from . import SelectionMixin,          \
              RotateMixin,             \
              SceneItemInteraction, \
              BlockPinInteraction,     \
              ItemType

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingScene


class PlaceBaseInteraction(
    SelectionMixin,       # _preserveSelection, _restoreSelection
    SceneItemInteraction  # _scene, _item, valid
):
    """Base for all interactions that place a single item."""

    # class attributes
    _ITEM : ItemType  # subclass to override with item class

    def __init__(
        self  : Self,
        scene : "DrawingScene",
        pos   : QPointF,
        item  : ItemType | None = None
    ) -> None:
        if item is None:
            item = self._ITEM(pos)
        else:
            item.setPos(pos)
        SceneItemInteraction.__init__(self, scene, item)
        self._preserveSelection()
        self._scene.clearSelection()
        self._scene.addItem(self._item)
        self._item.setSelected(True)

    def update(self : Self, pos : QPointF):
        self._item.setPos(pos)

    def complete(self : Self, pos : QPointF) -> bool:
        self.update(pos)
        self._scene.undo_stack.push(cmdAdd(
            self._scene, [self._item], self._selection
        ))
        return True

    def cancel(self : Self) -> None:
        self._scene.removeItem(self._item)
        self._restoreSelection()


class PlaceLineInteraction(PlaceBaseInteraction):
    _ITEM = Line

    # instance attributes
    _item : Line  # type hint specific to this interaction

    def update(self : Self, pos : QPointF):
        self._item.setP2(pos)


class PlaceBaseRectInteraction(PlaceBaseInteraction):
    """Base for all interactions that place a single rectangular item."""

    # instance attributes
    _item : BaseRectangle  # type hint specific to this interaction
    _pos  : QPointF        # initial position

    def __init__(
        self  : Self,
        scene : "DrawingScene",
        pos   : QPointF,
        item  : ItemType | None = None
    ) -> None:
        super().__init__(scene, pos, item)
        self._pos = pos

    def update(self : Self, pos : QPointF):
        self._item.setPoints(self._pos, pos)


class PlacePortInteraction(RotateMixin, PlaceBaseInteraction):
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


class PlaceBlockInteraction(PlaceBaseRectInteraction):
    _ITEM = Block


class PlaceBlockPinInteraction(BlockPinInteraction):
    def __init__(
        self   : Self,
        scene  : "DrawingScene",
        parent : Block,
        pin    : BlockPin,
        pos    : QPointF,
        snap   : QPointF | None = None
    ) -> None:
        BlockPinInteraction.__init__(self, scene, parent, pin, pos, snap)

    def update(self : Self, pos : QPointF, snap : QPointF | None = None) -> None:
        self._pin.setLoc(self._pin.locSnap(self._parent.pos2loc(pos), snap))

    def complete(self : Self, pos : QPointF, snap : QPointF | None = None) -> bool:
        self.update(pos, snap)
        self._scene.undo_stack.push(cmdAddBlockPin(self._parent, self._pin))
        return True

    def cancel(self : Self) -> None:
        self._pin.setParentItem(None)


class PlaceSymbolPinInteraction(PlaceBaseInteraction):
    _ITEM = SymbolPin


class PlaceRectangleInteraction(PlaceBaseRectInteraction):
    _ITEM = Rectangle


class PlaceTextInteraction(PlaceBaseInteraction):
    _ITEM = Text


class PlaceTextBlockInteraction(PlaceBaseInteraction):
    _ITEM = TextBlock


class PlaceConnInteraction(SelectionMixin):
    """Interactive wire placement involves two preview segments."""

    # instance attributes
    _scene : "DrawingScene"
    _seg1  : ConnSegPreview1
    _seg2  : ConnSegPreview2

    def __init__(
        self   : Self,
        scene  : "DrawingScene",
        pos    : QPointF
    ) -> None:
        self._scene = scene
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

    def complete(self : Self, pos : QPointF) -> bool:
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
        # create second segment if mouse is over a connectable destination
        if connectables_2:
            self._scene.addConnSeg(self._p1(), self._p2(), undo=True)
            self._cleanup()
            return True  # interaction completed
        self._restart(pos)
        return False  # continue interaction

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

    # todo: _commit method

    def _cleanup(self : Self) -> None:
        for item in [self._seg1, self._seg2]:
            self._scene.removeItem(item)
