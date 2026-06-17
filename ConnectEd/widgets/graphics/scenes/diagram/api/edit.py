from __future__ import annotations

from typing import Self, TypeAlias

from ......app import logger

from ......core.check import checked
from ......core.types import EdgeLoc

from ....items import ItemType

from ....items.block         import BlockItem
from ....items.block_pin     import BlockPinItem
from ....items.property_text import PropertyTextItem
from ....items.segment       import SegmentItem

from ...drawing.api import DrawingSceneApiEditMixin

from ...drawing.cmd import cmdExec

from ..cmd.block_pin import CmdMoveBlockPins

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DiagramScene
    MixinSelf: TypeAlias = Self | DiagramScene
else:
    MixinSelf = Self


class DiagramSceneApiEditMixin(DrawingSceneApiEditMixin):
    @checked
    def editMoveBlockPins(
        self     : MixinSelf,
        parent   : BlockItem,
        pins     : list[BlockPinItem],
        after    : dict[BlockPinItem, EdgeLoc],
        before   : dict[BlockPinItem, EdgeLoc],
        undoable : bool = False
    ) -> None:
        cmd = CmdMoveBlockPins(parent, pins, after, before)
        cmdExec(self, cmd, undoable)

    @checked
    def editDelete(
        self     : MixinSelf,
        items    : list[ItemType] | None = None,
        undoable : bool = False
    ) -> None:
        """Delete selected items from the scene; netlist aware."""
        if items is None:
            items = self._selectedTopItems()
        # filter out items with parents apart from property texts
        for item in items:
            if item.parentItem() is not None:
                if isinstance(item, PropertyTextItem):
                    continue
                items.remove(item)
        # check that there is something to do
        if items == []:
            logger().warning("No items to delete")
            return
        # start macro
        if undoable:
            self.undo_stack.beginMacro("editDelete")
        # remove segments (netlist aware)
        for item in items[:]:
            if isinstance(item, SegmentItem):
                self.removeSegment(item, undoable)
                items.remove(item)
        # delete remaining items
        if items:
            super().editDelete(items, undoable)
        # end macro
        if undoable:
            self.undo_stack.endMacro()
