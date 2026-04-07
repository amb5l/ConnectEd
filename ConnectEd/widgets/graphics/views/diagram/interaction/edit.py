from typing import Self

from PyQt6.QtCore import QPointF

from ......core.types import EdgeLoc

from ....items.block     import BlockItem
from ....items.block_pin import BlockPinItem

from ...drawing.interaction import Interaction

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...drawing import DrawingView


class EditMoveBlockPinsInteraction(Interaction):
    # instance attributes
    _parent : BlockItem
    _pins   : list[BlockPinItem]           # first item is primary pin
    _sloc   : dict[BlockPinItem, EdgeLoc]  # stored locations of all pins

    def __init__(
        self   : Self,
        view   : "DrawingView",
        parent : BlockItem,
        pins   : list[BlockPinItem]
    ) -> None:
        super().__init__(view)
        self._parent = parent
        self._pins = pins
        self._storeLoc()

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
        self._scene.editMoveBlockPins(
            self._parent,
            self._pins,
            {p: p.loc() for p in self._pins},
            self._sloc,
            undoable=True
        )
        return True

    def cancel(self : Self) -> None:
        self._restoreLoc()

    def _storeLoc(self : Self) -> None:
        self._sloc = {p: p.loc() for p in self._pins}

    def _restoreLoc(self : Self) -> None:
        for p in self._pins:
            p.setLoc(self._sloc[p])
