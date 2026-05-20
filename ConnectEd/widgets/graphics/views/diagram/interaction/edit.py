from typing import Self

from PyQt6.QtCore import QPointF

from ......core.check import checked
from ......core.types import EdgeLoc

from ....items.block     import BlockItem
from ....items.block_pin import BlockPinItem

from ...drawing.interaction import PreviewStateMixin, Interaction

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...diagram import DiagramView


class EditMoveBlockPinsInteraction(PreviewStateMixin, Interaction):
    # instance attributes
    _parent : BlockItem
    _pins   : list[BlockPinItem]  # first item is primary pin

    @checked
    def __init__(
        self   : Self,
        view   : "DiagramView",
        parent : BlockItem,
        pins   : list[BlockPinItem]
    ) -> None:
        super().__init__(view)
        self._parent = parent
        self._pins = pins
        self._previewSave()

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

    def _commit(self : Self, pos : QPointF, snap : QPointF | None = None) -> bool:
        self._previewRestore()
        self.update(pos, snap)
        if all(p.loc() == self._preview_state[p] for p in self._pins):
            return True # no change so skip command push
        self._scene.editMoveBlockPins(
            self._parent,
            self._pins,
            {p: p.loc() for p in self._pins},
            {p: self._preview_state[p] for p in self._pins},
            undoable=True
        )
        return True

    def _cancel(self : Self) -> None:
        self._previewRestore()

    def _previewTargets(self : Self) -> list[BlockPinItem]:
        return self._pins

    def _previewSaveTarget(self : Self, target : BlockPinItem) -> EdgeLoc:
        return target.loc()

    def _previewRestoreTarget(
        self   : Self,
        target : BlockPinItem,
        state  : EdgeLoc
    ) -> None:
        target.setLoc(state)
