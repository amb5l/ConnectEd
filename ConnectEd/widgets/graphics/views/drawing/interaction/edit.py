from typing import Self

from PyQt6.QtCore import QPointF

from ......core.xml import paste

from ....items import EdgeLoc, clone

from ....items.block     import Block
from ....items.block_pin import BlockPin

from ....scenes.drawing.cmd import CmdAdd, CmdMove, CmdMoveBlockPins

from . import MoveItemsMixin,      \
              AddRemoveItemsMixin, \
              SelectionMixin,      \
              ItemsInteraction,    \
              Interaction,         \
              ItemType

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...drawing import DrawingView


class EditPasteInteraction(
    MoveItemsMixin,       # update, _moveBy, _storePos, _restorePos
    AddRemoveItemsMixin,  # _addToScene, _removeFromScene
    SelectionMixin,       # _preserveSelection, _restoreSelection
    ItemsInteraction      # _view, _scene, _items, valid
):
    def __init__(
        self : Self,
        view : "DrawingView",
        pos  : QPointF
    ) -> None:
        items, copy_pos = paste()
        if items:
            ItemsInteraction.__init__(self, view, items)
            self._ipos = pos if copy_pos is None else copy_pos
            self._cpos = self._ipos
            self._preserveSelection()  # store prior selection set
            self._items = items
            self._storePos()
            self._addToScene(select=True)
            self.update(pos)  # Move to initial position
        else:
            self._items = None

    def commit(self : Self, pos : QPointF) -> bool:
        self._restorePos()  # restore initial positions
        self.update(pos)    # apply final offset
        # add pasted items to scene
        self._scene.undo_stack.push(CmdAdd(
            self._scene, self._items, self._selection
        ))
        return True

    def cancel(self : Self) -> None:
        self._removeFromScene()   # remove preview items
        self._restoreSelection()  # restore original selection


class EditDuplicateInteraction(EditPasteInteraction):
    """Very similar to paste, but items come from cloning."""

    def __init__(
        self  : Self,
        view  : "DrawingView",
        items : list[ItemType],  # items to duplicate
        pos   : QPointF          # duplication origin
    ) -> None:
        if items:
            ItemsInteraction.__init__(self, view, clone(items))
            self._ipos = pos
            self._cpos = pos
            self._preserveSelection()  # store prior selection set
            self._storePos()
            self._addToScene(select=True)
        else:
            self._items = None


class EditMoveInteraction(
    MoveItemsMixin,    # update, _moveBy, _storePos, _restorePos
    ItemsInteraction,  # _view, _scene, _items, valid
):
    # instance attributes
    _slide  : bool  # true => retain connections, false => break connections

    def __init__(
        self  : Self,
        view  : "DrawingView",
        items : list[ItemType],
        pos   : QPointF,
        slide : bool = False
    ) -> None:
        items = items if isinstance(items, list) else [items]
        ItemsInteraction.__init__(self, view, items)
        self._ipos     = pos
        self._cpos     = pos
        self._slide    = slide
        self._storePos()  # record initial positions

    def commit(self : Self, pos : QPointF) -> bool:
        self._restorePos()  # restore initial positions
        # apply final offset
        self._scene.undo_stack.push(CmdMove(
            self._scene, self._items, pos - self._ipos, self._slide
        ))
        return True

    def cancel(self : Self) -> None:
        self._restorePos()  # restore initial positions


class EditMoveBlockPinsInteraction(Interaction):
    # instance attributes
    _parent : Block
    _pins   : list[BlockPin]           # first item is primary pin
    _sloc   : dict[ItemType, EdgeLoc]  # stored locations of all pins

    def __init__(
        self   : Self,
        view   : "DrawingView",
        parent : Block,
        pins   : list[BlockPin]
    ) -> None:
        Interaction.__init__(self, view)
        self._parent = parent
        self._pins = pins
        self._storeLoc()

    @property
    def valid(self : Self) -> bool:
        return \
            self._parent is not None and \
            hasattr(self, "_pins") and \
            len(self._pins) > 0

    def update(self : Self, pos : QPointF, snap : QPointF | None = None) -> None:
        pos_snap = self._scene._snap(pos, snap) if snap else pos
        primary = self._pins[0]
        loc_old = primary.loc()
        loc_new = self._parent.pos2loc(pos)
        loc_new_snap = self._parent.pos2loc(pos_snap)
        offset = self._parent.locDelta(loc_old, loc_new_snap)
        snap_pressure = self._parent.locDelta(loc_new, loc_new_snap)
        corner = +1 if snap_pressure > 0 else -1 if snap_pressure < 0 else 0
        self._pins[0].setLoc(loc_new_snap)
        for pin in self._pins[1:]:
            pin.setLoc(self._parent.locOffset(pin.loc(), offset, corner))

    def commit(self : Self, pos : QPointF, snap : QPointF | None = None) -> bool:
        self._restoreLoc()
        self.update(pos, snap)
        if all(p.loc() == self._sloc[p] for p in self._pins):
            return True # no change so skip command push
        self._scene.undo_stack.push(CmdMoveBlockPins(
            self._parent,
            self._pins,
            {p: p.loc() for p in self._pins},
            self._sloc
        ))
        return True

    def cancel(self : Self) -> None:
        self._restoreLoc()

    def _storeLoc(self : Self) -> None:
        self._sloc = {p: p.loc() for p in self._pins}

    def _restoreLoc(self : Self) -> None:
        for p in self._pins:
            p.setLoc(self._sloc[p])
