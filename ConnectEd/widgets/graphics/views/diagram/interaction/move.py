from typing import Self, Any

from PyQt6.QtCore    import QPointF, QLineF, QRectF
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QUndoStack, QUndoCommand

from ......core.check import checked
from ......core.defs  import PITCH
from ......core.types import Axis, Polarity

from ....views.drawing.interaction import PreviewStateMixin

from ....items import ItemType

from ....items.port_pin import PortPinMixin
from ....items.node     import NodeItem, FreeNodeItem, FixedNodeItem
from ....items.segment  import SegmentItem
from ....items.gate     import GateItem
from ....items.block    import BlockItem
from ....items.symbol   import SymbolItem
from ....items.rubber   import RubberItem, \
                               RubberTeeItem, RubberCornerItem, RubberJogItem

from . import DiagramItemsInteraction

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....scenes.diagram import DiagramScene
    from ...diagram import DiagramView


MIN_JOG = 2  # pixels


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

    @checked
    def __init__(
        self  : Self,
        view  : "DiagramView",
        items : ItemType | list[ItemType],
        pos   : QPointF,                    # movement origin
        slide : bool = False
    ) -> None:
        self._ipos        = pos
        self._pos         = pos
        self._slide       = slide
        self._undo_stack  = QUndoStack()
        self._rubbers     = []
        self._rubber_jogs = []
        self._rubber_segs = []
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
                return item in item_set
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
                node2 = item.node2()
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
                        float_node = self._float(item, static_node)
                        filtered_items.append(float_node)
                else:
                    # mobile segment, 2 static nodes
                    filtered_items.append(item)
                    for node in (item.node1(), item.node2()):
                        if isinstance(node, FreeNodeItem) and node.degree() == 1:
                            filtered_items.append(node)
                        else:
                            float_node = self._float(item, node)
                            filtered_items.append(float_node)
                            if slide:
                                self._rubber(node, float_node)
            # handle items with pins:
            #  look for and rubberize connected segments not in item set
            # TODO: include net labels
            elif isinstance(item, GateItem | BlockItem | SymbolItem):
                filtered_items.append(item)
                for child in item.childItems():
                    if isinstance(child, PortPinMixin):
                        # process pin
                        node = child.node()
                        segs = node.segments()
                        for seg in segs:
                            # process connected segments
                            if seg not in item_set and seg.isOrthogonal():
                                self._rubber(seg, node)
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
        seen : set[ItemType] = set()
        unique_items : list[ItemType] = []
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
        self._moveBy(pos - self._pos)
        self._pos = pos
        self._updateJogs()

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
        # delete segments (those being moved, and those that were rubberized)
        if segments_to_delete:
            self._scene.editDelete(segments_to_delete, undoable=True)
        if self._rubber_segs:
            self._scene.editDelete(self._rubber_segs, undoable=True)
        # move remaining items
        if items:
            self._scene.editMove(items, offset, self._slide, undoable=True)
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

    def _previewSaveTarget(self : Self, target : ItemType) -> QPointF:
        return target.pos()

    @checked
    def _previewRestoreTarget(
        self   : Self,
        target : ItemType,
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
        if isinstance(segment_or_static, SegmentItem):
            segment = segment_or_static
            static  = segment.otherNode(mobile)
            if isinstance(static, FreeNodeItem):
                def _recordRubberSeg(segment : SegmentItem) -> None:
                    if segment not in self._rubber_segs:
                        self._rubber_segs.append(segment)
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
                self._rubbers.append(cmd.rubber())
                self._rubber_jogs.append(cmd.rubber())
                _recordRubberSeg(segment)
        elif isinstance(segment_or_static, NodeItem):
            static = segment_or_static
            cmd = CmdMovePreviewRubberJog(static, mobile, axis)
            self._undo_stack.push(cmd)
            self._rubbers.append(cmd.rubber())
            self._rubber_jogs.append(cmd.rubber())

    @checked
    def _float(
        self    : Self,
        segment : SegmentItem,
        node    : NodeItem
    ) -> FreeNodeItem:
        """
        Detach segment from specified node.
        """
        cmd = CmdMovePreviewFloatSegmentNode(segment, node)
        self._undo_stack.push(cmd)
        return cmd.node()

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
                if _conflict(rect1, jog_rects[jog2], jog1.axis()):
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

            # classify + spatial sort key
            quad_to_jogs: dict[tuple[Polarity, Polarity], list[RubberJogItem]] = {}
            jog_quad: dict[RubberJogItem, tuple[ Polarity, Polarity]] = {}
            jog_across_center: dict[RubberJogItem, float] = {}

            for jog in group:
                q = (jog.inlinePolarity(), jog.acrossPolarity())
                jog_quad[jog] = q
                jog_across_center[jog] = jog.acrossCenter()
                quad_to_jogs.setdefault(q, []).append(jog)

            # sort inside each quadrant by across position → cascading staircases
            for jogs in quad_to_jogs.values():
                jogs.sort(key=lambda j: jog_across_center[j])

            # order quadrants spatially (keeps "i+a- block then i+a+ block" coherent)
            # using lambda avoids the "does not bind loop variable" checker warning
            ordered_quads = sorted(
                quad_to_jogs.keys(),
                key=lambda q: (
                    min(jog_across_center[j] for j in quad_to_jogs[q])
                    if quad_to_jogs[q]
                    else 0.0
                ),
            )

            # final ordered list: same-quadrant jogs stay together + spatially ordered
            ordered_jogs: list[RubberJogItem] = []
            for q in ordered_quads:
                ordered_jogs.extend(quad_to_jogs[q])

            n = len(ordered_jogs)
            if n <= 1:
                continue

            prefs = [j.preferredLane() for j in ordered_jogs]
            base = sum(prefs) / n
            total_grid_span = (n - 1) * PITCH

            # available room heuristic
            room = min(j.inlineDistance() for j in ordered_jogs)
            margin = 2 * PITCH

            if total_grid_span > room - margin:
                # fallback: even arithmetic distribution in observed preferred span
                min_p = min(prefs)
                max_p = max(prefs)
                step = (max_p - min_p) / (n - 1) if n > 1 and max_p > min_p else 0.0
                for i, jog in enumerate(ordered_jogs):
                    jog.setLane(min_p + i * step)
            else:
                # nice grid placement, centered on group
                start = round((base - total_grid_span / 2) / PITCH) * PITCH
                for i, jog in enumerate(ordered_jogs):
                    jog.setLane(start + i * PITCH)

        # --- 5. final path update for everyone ---------------------------------
        for jog in self._rubber_jogs:
            jog.updatePath()


class CmdMovePreviewFloatSegmentNode(QUndoCommand):
    _scene    : "DiagramScene"
    _segment  : SegmentItem
    _node_old : NodeItem
    _node_new : NodeItem

    def __init__(
        self    : Self,
        segment : SegmentItem,  # segment to detach
        node    : NodeItem      # node to detach from
    ) -> None:
        """
        Preview command: detach a segment from a node, replacing it with a new
        free node.

        Args:
            segment: Segment to detach.
            node:    Existing endpoint node to float away from.
        """
        super().__init__()
        self._scene    = segment.scene()
        self._segment  = segment
        self._node_old = node
        self._node_new = FreeNodeItem(node.scenePos())

    def redo(self : Self) -> None:
        self._scene.addItem(self._node_new)
        self._segment.changeNode(self._node_old, self._node_new)

    def undo(self : Self) -> None:
        self._segment.changeNode(self._node_new, self._node_old)
        self._scene.removeItem(self._node_new)

    def node(self : Self) -> NodeItem:
        return self._node_new


class CmdMovePreviewRubberBase(QUndoCommand):
    _scene   : "DiagramScene"
    _rubber  : RubberItem

    def __init__(
        self   : Self,
        scene  : "DiagramScene",
        rubber : RubberItem
    ) -> None:
        super().__init__()
        self._scene  = scene
        self._rubber = rubber

    def rubber(self : Self) -> RubberItem:
        return self._rubber


class CmdMovePreviewRubberTee(CmdMovePreviewRubberBase):
    _segment : SegmentItem
    _rubber  : RubberTeeItem

    def __init__(self : Self, segment : SegmentItem, node : NodeItem) -> None:
        super().__init__(segment.scene(), RubberTeeItem(segment, node))
        self._segment = segment

    def redo(self : Self) -> None:
        self._scene.addItem(self._rubber)
        self._scene.removeItem(self._segment)

    def undo(self : Self) -> None:
        self._scene.addItem(self._segment)
        self._scene.removeItem(self._rubber)


class CmdMovePreviewRubberCorner(CmdMovePreviewRubberBase):
    _segment1 : SegmentItem
    _segment2 : SegmentItem
    _corner   : FreeNodeItem
    _rubber   : RubberCornerItem

    def __init__(
        self     : Self,
        segment1 : SegmentItem,
        segment2 : SegmentItem,
        node     : NodeItem
    ) -> None:
        """
        Preview command: replace a segment with a rubber corner.

        Args:
            segment1: Segment attached to mobile node.
            segment2: Segment attached to corner.
            node:     Mobile node.
        """
        super().__init__(
            segment1.scene(),
            RubberCornerItem(segment1, segment2, node)
        )
        self._segment1 = segment1
        self._segment2 = segment2
        self._corner   = segment1.otherNode(node)

    def redo(self : Self) -> None:
        self._scene.addItem(self._rubber)
        self._scene.removeItem(self._segment1)
        self._scene.removeItem(self._segment2)
        self._scene.removeItem(self._corner)

    def undo(self : Self) -> None:
        self._scene.addItem(self._corner)
        self._scene.addItem(self._segment1)
        self._scene.addItem(self._segment2)
        self._scene.removeItem(self._rubber)


class CmdMovePreviewRubberJog(CmdMovePreviewRubberBase):
    _segment_or_static : SegmentItem | NodeItem
    _rubber            : RubberJogItem

    def __init__(
        self              : Self,
        segment_or_static : SegmentItem | NodeItem,
        mobile            : NodeItem,
        axis              : Axis | None = None
    ) -> None:
        """
        Preview command: replace a segment with a rubber jog, or add one between
        a static node and a mobile node.

        Args:
            segment_or_node: Segment to replace or static node.
            node: Mobile node.
            axis: Jog inline axis (optional).
        """
        super().__init__(
            mobile.scene(),
            RubberJogItem(segment_or_static, mobile, axis)
        )
        self._segment_or_static = segment_or_static

    def redo(self : Self) -> None:
        self._scene.addItem(self._rubber)
        if self._segment_or_static is not None:
            self._scene.removeItem(self._segment_or_static)

    def undo(self : Self) -> None:
        if self._segment_or_static is not None:
            self._scene.addItem(self._segment_or_static)
        self._scene.removeItem(self._rubber)
