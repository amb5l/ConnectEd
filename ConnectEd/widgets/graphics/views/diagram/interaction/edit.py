from typing import Self

from PyQt6.QtCore import QPointF
from PyQt6.QtGui  import QUndoStack

from ......core.check import checked
from ......core.types import EdgeLoc

from ....items.block     import BlockItem
from ....items.block_pin import BlockPinItem

from ....scenes.diagram.cmd.conn import CmdDetachSegmentNode

from ...drawing.interaction import PreviewStateMixin

from . import DiagramInteraction

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...diagram import DiagramView


class DiagramEditMoveBlockPinsInteraction(PreviewStateMixin, DiagramInteraction):
    # instance attributes
    _undo_stack : QUndoStack          # private undo stack for preview
    _block      : BlockItem
    _pins       : list[BlockPinItem]  # first item is primary pin | None
    _loc_snap   : EdgeLoc | None
    _corner     : int | None

    @checked
    def __init__(
        self  : Self,
        view  : "DiagramView",
        block : BlockItem,
        pins  : list[BlockPinItem]
    ) -> None:
        super().__init__(view)
        self._block    = block
        self._pins     = pins
        self._loc_snap = None
        self._corner   = None
        self._undo_stack = QUndoStack()
        for pin in self._pins:
            for seg in list(pin.node().segments()):
                self._undo_stack.push(
                    CmdDetachSegmentNode(self._scene, seg, pin.node())
                )
        self._previewSave()

    def valid(self : Self) -> bool:
        return \
            self._block is not None and \
            hasattr(self, "_pins") and \
            len(self._pins) > 0

    def update(self : Self, pos : QPointF, snap : QPointF | None = None) -> None:
        pos_snap = self._scene._snap(pos, snap) if snap else pos
        primary = self._pins[0]
        loc_old = primary.loc()
        loc_new = self._block.pos2loc(pos)
        loc_new_snap = self._block.pos2loc(pos_snap)
        offset = self._block.locDelta(loc_old, loc_new_snap)
        snap_pressure = self._block.locDelta(loc_new, loc_new_snap)
        corner = +1 if snap_pressure > 0 else -1 if snap_pressure < 0 else 0
        if loc_new_snap == self._loc_snap and corner == self._corner:
            return  # filter redundant updates
        self._pins[0].setLoc(loc_new_snap)
        for pin in self._pins[1:]:
            pin.setLoc(self._block.locOffset(pin.loc(), offset, corner))
        self._loc_snap = loc_new_snap
        self._corner = corner

    def _commit(self : Self, pos : QPointF, snap : QPointF | None = None) -> bool:
        self.update(pos, snap)
        after  = {p: p.loc() for p in self._pins}
        before = {p: self._preview_state[p] for p in self._pins}
        if after == before:
            self._cancel()
            return True  # no change so skip command push
        self._previewRestore()
        self._undo_stack.setIndex(0)
        self._scene.undo_stack.beginMacro("editMoveBlockPins")
        for pin in self._pins:
            self._scene.detachFixedNode(pin.node(), undoable=True)
        self._scene.editMoveBlockPins(
            self._block,
            self._pins,
            after,
            before,
            undoable=True
        )
        for pin in self._pins:
            self._scene.connectFixedNode(pin.node(), undoable=True)
        self._scene.undo_stack.endMacro()
        return True

    def _cancel(self : Self) -> None:
        self._previewRestore()
        self._undo_stack.setIndex(0)

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

    def _previewDidRestore(self : Self) -> None:
        self._loc_snap = None
        self._corner   = None
