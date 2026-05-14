from ......app import logger

from ......core.types import EdgeLoc

from ....items import ItemType

from ....items.block          import BlockItem
from ....items.block_pin      import BlockPinItem
from ....items.node           import FixedNodeItem
from ....items.property_text  import PropertyTextItem
from ....items.property_label import PropertyLabelItem
from ....items.segment        import SegmentItem

from ...drawing.api import DrawingSceneApiEditMixin

from ...drawing.cmd import cmdExec

from ..cmd.block_pin import CmdMoveBlockPins

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DiagramScene


class DiagramSceneApiEditMixin(DrawingSceneApiEditMixin):
    def editMoveBlockPins(
        self     : "DiagramScene",
        parent   : BlockItem,
        pins     : list[BlockPinItem],
        after    : dict[BlockPinItem, EdgeLoc],
        before   : dict[BlockPinItem, EdgeLoc],
        undoable : bool = False
    ) -> None:
        cmd = CmdMoveBlockPins(parent, pins, after, before)
        cmdExec(self, cmd, undoable)

    def editDelete(
        self     : "DiagramScene",
        items    : list[ItemType] | None = None,
        undoable : bool = False
    ) -> None:
        """Delete selected items from the scene; netlist aware."""
        if items is None:
            items = self._selectedTopItems()
        # filter out items with parents apart from property texts/labels
        for item in items:
            if item.parentItem() is not None:
                if isinstance(item, PropertyTextItem | PropertyLabelItem):
                    continue
                items.remove(item)
        # check that there is something to do
        if items == []:
            logger().warning("No items to delete")
            return
        # start macro
        if undoable:
            self.undo_stack.beginMacro("editDelete")
        # remove segments and orphan free nodes
        for item in items:
            if isinstance(item, SegmentItem):
                self.removeSegment(item, undoable)
                for vtx in [item.node1(), item.node2()]:
                    if vtx is not None \
                    and vtx.parentItem() is None \
                    and vtx.degree() == 0:
                        self.removeFreeNode(vtx, undoable)
        # gather fixed nodes
        fixed_nodes = []
        for item in items:  # may include items with pins or entries
            for child in item.childItems():  # may include pins or entries
                if isinstance(child, FixedNodeItem):
                    fixed_nodes.append(child)
                for grandchild in child.childItems():  # may include entries
                    if isinstance(grandchild, FixedNodeItem):
                        fixed_nodes.append(grandchild)
        #
        # end macro
        if undoable:
            self.undo_stack.endMacro()
