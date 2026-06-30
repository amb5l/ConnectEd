from __future__ import annotations

from typing import Self, Any

from PyQt6.QtCore    import QPointF, QLineF, QRectF
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QUndoStack

from ......core.check import checked
from ......core.defs  import PITCH
from ......core.types import Axis, Polarity, EdgeLoc

from ....views.diagram.interaction import PreviewStateMixin

from ....items.port_pin  import PortPinMixin
from ....items.node      import NodeItem, FreeNodeItem, FixedNodeItem
from ....items.segment   import SegmentItem
from ....items.tap       import TapItem
from ....items.port      import PortItem
from ....items.gate      import GateItem
from ....items.block     import BlockItem
from ....items.block_pin import BlockPinItem
from ....items.symbol    import SymbolInstanceItem
from ....items.rubber    import RubberItem, RubberJogItem

from ....scenes.diagram import DiagramScene

from ....scenes.diagram.cmd.conn   import CmdDetachSegmentNode
from ....scenes.diagram.cmd.rubber import (
    CmdMovePreviewRubberTee,
    CmdMovePreviewRubberCorner,
    CmdMovePreviewRubberJog
)

from . import DiagramInteraction, DiagramItemsInteraction

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...diagram import DiagramView


MIN_JOG = 2  # pixels


def _staircaseReverse(
    axis   : Axis,
    inline : Polarity,
    across : Polarity,
) -> bool:
    """
    True when lane indices should run opposite to ascending across-center order.

    For horizontal jogs (inline along X), wires that bend downward need the
    upper static endpoint on the outer lane; wires bending upward need it on the
    inner lane. Vertical jogs mirror the same rule on Y.
    """
    return (axis == Axis.H) == (inline == across)


def _jogsShareStaircase(j1 : RubberJogItem, j2 : RubberJogItem) -> bool:
    """
    True when two jogs route in parallel along the same inline span and need
    separated lanes even if their preview bounds do not yet intersect.
    """
    if j1.axis() != j2.axis():
        return False
    if j1.inlinePolarity() != j2.inlinePolarity():
        return False
    s1 = j1.inlineSpan()
    s2 = j2.inlineSpan()
    return s1[0] < s2[1] and s2[0] < s1[1]


class DiagramMoveInteraction(PreviewStateMixin, DiagramItemsInteraction):
    """
    Full-blown move with rubber band support. Uses private undo stack.

    Sequence:
    - filter out items that have ancestors
    - remove bridge segments from scene, replace with rubber preview items
    - on commit:
      - remove rubber preview items from scene
      - restore original positions
      - restore bridge segments to scene
      - remove all segments and nodes from item set,
          recording all rigid segments for recreation below
      - delete all segments (rigid and rubber)*
      - move items*
      - redraw all segments in new position*
      - create new segments from rubber preview items*

    * = using undoable scene API


    """

    # instance attributes
    _undo_stack  : QUndoStack           # private undo stack for preview operations
    _ipos        : QPointF              # initial position
    _pos         : QPointF | None       # last position (filter redundant updates)
    _slide       : bool                 # true => retain connections
    _rubbers     : list[RubberItem]     # all rubber items
    _rubber_jogs : list[RubberJogItem]  # rubber jog items
    _rubber_segs : list[SegmentItem]    # rubberized segments
    _move_segs   : list[SegmentItem]    # moved segments
    _detached_segs : list[tuple[SegmentItem, FixedNodeItem]]

    @checked
    def __init__(
        self  : Self,
        view  : DiagramView,
        items : QGraphicsItem | list[QGraphicsItem],
        pos   : QPointF,                    # movement origin
        slide : bool = False
    ) -> None:
        scene = view.scene()
        if not isinstance(scene, DiagramScene):
            raise TypeError("Bad scene")
        self._view          = view
        self._scene         = scene
        self._ipos          = pos
        self._pos           = pos
        self._slide         = slide
        self._undo_stack    = QUndoStack()
        self._rubbers       = []
        self._rubber_jogs   = []
        self._rubber_segs   = []
        self._detached_segs = []
        # process items
        if not isinstance(items, list):
            items = [items]
        item_set = set(items)
        filtered_items = []
        def _mobile(node : NodeItem) -> bool:
            """
            Is node a member of, or does it belong to a member of, the item set.
            """
            if isinstance(node, FixedNodeItem):
                pin : PortPinMixin | QGraphicsItem | None = node.parentItem()
                if pin in item_set:
                    return True
                if pin is not None:
                    pin_parent = pin.parentItem()
                    return pin_parent in item_set
            elif isinstance(node, FreeNodeItem):
                return node in item_set
            return False
        for item in item_set:
            # skip nodes (free nodes are handled in segment logic below)
            if isinstance(item, NodeItem):
                continue
            # handle segments
            # include those whose nodes are both in the item set,
            # and those with 1 or 2 static unconnected nodes;
            # rubberize others
            # TODO: include net labels
            elif isinstance(item, SegmentItem):
                node1 = item.node1()
                if node1 is None:
                    raise TypeError("node1 is None")
                node2 = item.node2()
                if node2 is None:
                    raise TypeError("node2 is None")
                mobile1 = _mobile(node1)
                mobile2 = _mobile(node2)
                if mobile1 and mobile2:
                    # mobile segment, mobile nodes
                    filtered_items.append(item)
                    if isinstance(node1, FreeNodeItem):
                        filtered_items.append(node1)
                    if isinstance(node2, FreeNodeItem):
                        filtered_items.append(node2)
                elif mobile1 != mobile2:
                    # mobile segment, 1 mobile node and 1 static node
                    mobile_node, static_node = \
                        (node1, node2) if mobile1 else (node2, node1)
                    if static_node.degree() == 1:
                        # special case: unconnected end
                        filtered_items.append(item)
                        filtered_items.append(static_node)
                    elif slide:
                        self._rubber(item, mobile_node)
                        if isinstance(mobile_node, FreeNodeItem):
                            filtered_items.append(mobile_node)
                    else:
                        filtered_items.append(item)
                        free_node = self._detachSegmentNode(item, static_node)
                        filtered_items.append(free_node)
                else:
                    # mobile segment, 2 static nodes
                    filtered_items.append(item)
                    for node in (node1, node2):
                        if isinstance(node, FreeNodeItem) and node.degree() == 1:
                            filtered_items.append(node)
                        else:
                            free_node = self._detachSegmentNode(item, node)
                            filtered_items.append(free_node)
                            if slide:
                                self._rubber(node, free_node)
            # handle items with fixed nodes (taps, ports, pins):
            #  look for and rubberize connected segments not in item set
            # TODO: include net labels
            elif isinstance(
                item,
                TapItem | PortItem | GateItem | BlockItem | SymbolInstanceItem
            ):
                def _processFixedNode(node : FixedNodeItem) -> None:
                    for seg in list(node.segments()):
                        if seg in item_set:
                            continue
                        if seg.isOrthogonal() and self._slide:
                            self._rubber(seg, node)
                        else:
                            self._detachSegmentNode(seg, node)
                            self._detached_segs.append((seg, node))
                filtered_items.append(item)
                if isinstance(item, TapItem):
                    _processFixedNode(item.majorNode())
                    _processFixedNode(item.minorNode())
                elif isinstance(item, PortItem):
                    _processFixedNode(item.node())
                else:
                    for child in item.childItems():
                        if isinstance(child, PortPinMixin):  # pin
                            node = child.node()
                            _processFixedNode(node)
            # filter out items with ancestors in the items list
            else:
                parent = item.parentItem()
                while parent is not None:
                    if parent in item_set:
                        break
                    parent = parent.parentItem()
                else:
                    filtered_items.append(item)
        # deduplicate items
        seen : set[QGraphicsItem] = set()
        unique_items : list[QGraphicsItem] = []
        for item in filtered_items:
            if item not in seen:
                seen.add(item)
                unique_items.append(item)
        filtered_items = unique_items
        # complete interaction initialization
        super().__init__(view, filtered_items)
        # save initial positions
        self._previewSave()

    @checked
    def update(self : Self, pos : QPointF) -> None:
        if pos == self._pos:
            return  # filter redundant updates#
        if isinstance(self._pos, QPointF):
            self._moveBy(pos - self._pos)
            self._updateJogs()
        self._pos = pos

    @checked
    def _cancel(self : Self) -> None:
        # revert movement
        self._previewRestore()
        # undo rubber replacements/additions and segment floatations
        self._undo_stack.setIndex(0)

    @checked
    def _commit(self : Self, pos : QPointF) -> bool:
        # get final offset
        offset = pos - self._ipos
        if offset == QPointF(0, 0):
            self._cancel()
            return True  # no change so skip command push
        # revert preview movement, undo rubber/float operations
        self._cancel()
        # for segments to be moved (not rubberized):
        # - record line geometry for later recreation after applying offset
        # - record instances for later deletion
        # - remove from item set along with any free nodes
        items = list(self._items)  # local copy
        segments_to_recreate : list[QLineF] = []
        segments_to_delete : list[SegmentItem] = []
        for item in list(items):  # iterate over copy of copy (b/c mutation)
            if isinstance(item, SegmentItem):
                segments_to_recreate.append(item.sceneLine())
                segments_to_delete.append(item)
                node1 = item.node1()
                node2 = item.node2()
                items.remove(item)
                if isinstance(node1, FreeNodeItem) and node1 in items:
                    items.remove(node1)
                if isinstance(node2, FreeNodeItem) and node2 in items:
                    items.remove(node2)
        # start undoable sequence (macro)
        self._scene.undo_stack.beginMacro("editMove")
        for segment, fixed_node in self._detached_segs:
            self._scene.detachSegmentNode(segment, fixed_node, undoable=True)
        # delete segments (those being moved, and those that were rubberized)
        if segments_to_delete:
            self._scene.editDelete(segments_to_delete, undoable=True)
        if self._rubber_segs:
            self._scene.editDelete(self._rubber_segs, undoable=True)
        # move remaining items
        if items:
            self._scene.editMove(items, offset, self._slide, undoable=True)
        if self._slide:
            fixed_nodes : list[FixedNodeItem] = []
            for item in items:
                if isinstance(item, TapItem):
                    fixed_nodes.append(item.majorNode())
                    fixed_nodes.append(item.minorNode())
                elif isinstance(item, PortItem):
                    fixed_nodes.append(item.node())
                elif isinstance(item, GateItem | BlockItem | SymbolInstanceItem):
                    for child in item.childItems():
                        if isinstance(child, PortPinMixin):
                            fixed_nodes.append(child.node())
            self._scene.connectFixedNodes(fixed_nodes, undoable=True)
        # recreate moved segments in their new positions
        for segment_line in segments_to_recreate:
            p1 = segment_line.p1() + offset
            p2 = segment_line.p2() + offset
            self._scene.addSegment(p1, p2, undoable=True)
        # materialize segments from rubber
        self._updateJogs()  # others will update b/c subscribed to moved nodes
        for rubber in self._rubbers:
            for line in rubber.geometry():
                self._scene.addSegment(line.p1(), line.p2(), undoable=True)
        # end undoable sequence (macro)
        self._scene.undo_stack.endMacro()
        return True

    @checked
    def _complete(self : Self, pos : QPointF) -> None:
        self.commit(pos)

    @checked
    def _moveBy(self : Self, offset : QPointF) -> None:
        """
        Move all items by the specified offset.
        """
        for item in self._items:
            if isinstance(item, SegmentItem):
                continue  # geometry follows endpoint nodes via onGeometryChanged
            item.setPos(item.pos() + offset)

    def _previewTargets(self : Self) -> list[Any]:
        return [
            item for item in self._items
            if not isinstance(item, SegmentItem)
        ]

    def _previewSaveTarget(self : Self, target : QGraphicsItem) -> QPointF:
        return target.pos()

    @checked
    def _previewRestoreTarget(
        self   : Self,
        target : QGraphicsItem,
        state  : QPointF
    ) -> None:
        target.setPos(state)

    @checked
    def _rubber(
        self              : Self,
        segment_or_static : SegmentItem | NodeItem,  # segment or static node
        mobile            : NodeItem,                # mobile node
        axis              : Axis | None = None       # (optional) jog inline axis
    ) -> None:
        """
        Replace a segment with rubber, or add rubber between 2 nodes.

        Args:
            segment_or_node: Segment to rubberize or static node.
            node:            Mobile node.
            axis:            Jog inline axis (optional).
        """
        def _recordRubberSeg(segment : SegmentItem) -> None:
            if segment not in self._rubber_segs:
                self._rubber_segs.append(segment)

        if isinstance(segment_or_static, SegmentItem):
            segment = segment_or_static
            static  = segment.otherNode(mobile)
            if isinstance(static, FreeNodeItem):
                # TODO: should never get here with degree == 1, but handle it anyway
                if static.degree() == 2:
                    s1, s2 = static.segments()
                    segment2 = s1 if s2 is segment else s2
                    cmd = CmdMovePreviewRubberCorner(segment, segment2, mobile)
                    self._undo_stack.push(cmd)
                    self._rubbers.append(cmd.rubber())
                    _recordRubberSeg(segment)
                    _recordRubberSeg(segment2)
                else:
                    cmd = CmdMovePreviewRubberTee(segment, mobile)
                    self._undo_stack.push(cmd)
                    self._rubbers.append(cmd.rubber())
                    _recordRubberSeg(segment)
            else:
                cmd = CmdMovePreviewRubberJog(segment, mobile)
                self._undo_stack.push(cmd)
                rubber = cmd.rubber()
                self._rubbers.append(rubber)
                self._rubber_jogs.append(rubber)
                _recordRubberSeg(segment)
        elif isinstance(segment_or_static, NodeItem):
            static = segment_or_static
            cmd = CmdMovePreviewRubberJog(static, mobile, axis)
            self._undo_stack.push(cmd)
            self._rubbers.append(cmd.rubber())
            self._rubber_jogs.append(cmd.rubber())

    @checked
    def _detachSegmentNode(
        self    : Self,
        segment : SegmentItem,
        node    : NodeItem
    ) -> FreeNodeItem:
        """
        Detach segment from specified node.
        """
        cmd = CmdDetachSegmentNode(self._scene, segment, node)
        self._undo_stack.push(cmd)
        return cmd.freeNode()

    def _updateJogs(self: Self) -> None:
        """
        Update rubber jogs to avoid shorts after mobile nodes have moved.
        External routing lane conflicts are still resolved by the caller.
        """
        if not self._rubber_jogs:
            return

        # --- 1. bounding rects -------------------------------------------------
        jog_rects: dict[RubberJogItem, QRectF] = {
            jog: jog.mapToScene(jog.boundingRect()).boundingRect()
            for jog in self._rubber_jogs
        }

        # --- 2. build clean conflict groups (connected components, same axis) --
        groups: list[list[RubberJogItem]] = []
        processed: set[RubberJogItem] = set()
        jog_list = list(jog_rects.keys())

        def _conflict(rect1: QRectF, rect2: QRectF, axis: Axis) -> bool:
            if rect1.intersects(rect2):
                return True
            # inline edges touch (not just corner)
            if axis == Axis.H:
                if (rect1.top() == rect2.bottom() or rect1.bottom() == rect2.top()) and \
                   rect1.left() < rect2.right() and rect1.right() > rect2.left():
                    return True
            else:
                if (rect1.left() == rect2.right() or rect1.right() == rect2.left()) and \
                   rect1.top() < rect2.bottom() and rect1.bottom() > rect2.top():
                    return True
            return False

        for i, jog1 in enumerate(jog_list):
            if jog1 in processed:
                continue
            rect1 = jog_rects[jog1]
            group: list[RubberJogItem] = [jog1]
            processed.add(jog1)
            for jog2 in jog_list[i + 1 :]:
                if jog2 in processed:
                    continue
                if jog2.axis() != jog1.axis():
                    continue
                if (axis1 := jog1.axis()) is None:
                    continue
                if _jogsShareStaircase(jog1, jog2) \
                or _conflict(rect1, jog_rects[jog2], axis1):
                    group.append(jog2)
                    processed.add(jog2)
            groups.append(group)

        # --- 3. mark degenerates (isolated get 2×PITCH, clusters get 3×PITCH) --
        for group in groups:
            is_isolated = len(group) == 1
            thresh = 2 * PITCH if is_isolated else 3 * PITCH
            to_remove: list[RubberJogItem] = []
            for jog in group:
                if jog.inlineDistance() < thresh:
                    jog.setLane(None)
                    to_remove.append(jog)
            for jog in to_remove:
                group.remove(jog)

        # --- 4. quadrant-aware lane resolution ---------------------------------
        for group in groups:
            if len(group) <= 1:
                continue

            group_axis = group[0].axis()
            quad_to_jogs: dict[tuple[Polarity, Polarity], list[RubberJogItem]] = {}
            jog_across_center: dict[RubberJogItem, float] = {}

            for jog in group:
                q = (jog.inlinePolarity(), jog.acrossPolarity())
                jog_across_center[jog] = jog.acrossCenter()
                quad_to_jogs.setdefault(q, []).append(jog)

            ordered_quads = sorted(
                quad_to_jogs.keys(),
                key=lambda q: (
                    min(jog_across_center[j] for j in quad_to_jogs[q])
                    if quad_to_jogs[q]
                    else 0.0
                ),
            )

            for q in ordered_quads:
                jogs = quad_to_jogs[q]
                jogs.sort(key=lambda j: jog_across_center[j])
                n = len(jogs)
                if n <= 1:
                    continue

                reverse = _staircaseReverse(group_axis or Axis.H, q[0], q[1])
                prefs = [j.prefLane() for j in jogs]
                base = sum(prefs) / n
                total_grid_span = (n - 1) * PITCH
                room = min(j.inlineDistance() for j in jogs)
                margin = 2 * PITCH

                if total_grid_span > room - margin:
                    min_p = min(prefs)
                    max_p = max(prefs)
                    step = (max_p - min_p) / (n - 1) if n > 1 and max_p > min_p else 0.0
                    for i, jog in enumerate(jogs):
                        j = (n - 1 - i) if reverse else i
                        jog.setLane(min_p + j * step)
                else:
                    start = round((base - total_grid_span / 2) / PITCH) * PITCH
                    for i, jog in enumerate(jogs):
                        j = (n - 1 - i) if reverse else i
                        jog.setLane(start + j * PITCH)

        # --- 5. final path update for everyone ---------------------------------
        for jog in self._rubber_jogs:
            jog.updatePath()


class DiagramMoveBlockPinsInteraction(PreviewStateMixin, DiagramInteraction):
    # instance attributes
    _undo_stack : QUndoStack          # private undo stack for preview
    _block      : BlockItem
    _pins       : list[BlockPinItem]  # first item is primary pin | None
    _loc_snap   : EdgeLoc | None
    _corner     : int | None

    @checked
    def __init__(
        self  : Self,
        view  : DiagramView,
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
        pos_snap = self._scene._snap(pos, snap) if snap is not None else pos
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

    @checked
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
