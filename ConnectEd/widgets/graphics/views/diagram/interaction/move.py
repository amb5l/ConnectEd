from tkinter import N
from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QUndoStack

from ......core.check import checked

from ....items import ItemType

from ....items.port_pin import PortPinMixin
from ....items.node     import NodeItem, FreeNodeItem, FixedNodeItem
from ....items.segment  import SegmentItem

from . import DiagramItemsInteraction

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...diagram import DiagramView


class DiagramMoveInteraction(DiagramItemsInteraction):
    """Full-blown move with rubber band support. Uses private undo stack."""

    # instance attributes
    _undo_stack : QUndoStack      # private undo stack for preview operations
    _pos        : QPointF | None  # last position (to filter redundant updates)

    @checked
    def __init__(
        self  : Self,
        view  : "DiagramView",
        items : ItemType | list[ItemType],
        pos   : QPointF,                    # movement origin
        slide : bool = False
    ) -> None:
        self._undo_stack = QUndoStack()
        self._pos = pos
        # process items
        if not isinstance(items, list):
            items = [items]
        item_set = set(items)
        filtered_items = []
        def _mobile(node : NodeItem) -> bool:
            """
            Is node is part of, or does it belong to an item in, the item set.
            """
            if isinstance(node, FixedNodeItem):
                pin : PortPinMixin | QGraphicsItem | None = node.parentItem()
                if pin in item_set:
                    return True
                if pin is not None:
                    pin_parent = pin.parentItem()
                    return pin_parent in item_set
            elif isinstance(node, FreeNodeItem):
                return item in item_set
            return False
        for item in item_set:
            # ignore nodes (they are handled by segment processing below)
            if isinstance(item, NodeItem):
                continue
            # handle segments
            elif isinstance(item, SegmentItem):
                node1 = item.node1()
                node2 = item.node2()
                if _mobile(node1) and _mobile(node2):
                    # segment will be moved as a whole => include free node(s)
                    if isinstance(node1, FreeNodeItem):
                        filtered_items.append(node1)
                    if isinstance(node2, FreeNodeItem):
                        filtered_items.append(node2)
                elif _mobile(node1) and not _mobile(node2):
                    # node 1 in move set, node 2 not
                    self._rubberize1(item, node2, node1)
                    if isinstance(node1, FreeNodeItem):
                        filtered_items.append(node1)
                elif _mobile(node2) and not _mobile(node1):
                    # node2 mobile, node 1 static
                    self._rubberize1(item, node1, node2)
                    if isinstance(node2, FreeNodeItem):
                        filtered_items.append(node2)
                else:
                    # special case: static nodes, mobile segment
                    pass
            # filter out items with ancestors in the items list
            else:
                parent = item.parentItem()
                while parent is not None:
                    if parent in item_set:
                        break
                    parent = parent.parentItem()
                else:
                    filtered_items.append(item)
        if slide:
            pass
            # rubberize
        else:
            # detach all connected-but-unselected segments
            pass
        # complete interaction initialization
        super().__init__(view, filtered_items)

    def update(self : Self, pos : QPointF) -> None:
        if pos == self._pos:
            return  # filter redundant updates
        self._moveBy(pos - self._pos)
        self._pos = pos

    def _rubberize1(self : Self, static : NodeItem, mobile : NodeItem) -> None:
        # remove segment

        self._undo_stack.push(CmdRubberize1(self._scene, static, mobile))

        # add DCP to scene (undoable)


QUndoCommands to support move interaction:
- move subcommand can merge so stack ends up with
  - remove segment, add DCP x N
  - move