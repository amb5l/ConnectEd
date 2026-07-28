from __future__ import annotations

from typing import Self, TypeVar, Generic

from PyQt6.QtGui import QUndoCommand

from ......app import logger

from ......core.check import checked
from ......core.types import Axis

from ....items.node    import NodeItem, FreeNodeItem
from ....items.segment import SegmentItem
from ....items.rubber  import RubberItem, \
                              RubberTeeItem, RubberCornerItem, RubberJogItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....scenes.diagram import DiagramScene


TRubber = TypeVar("TRubber", bound=RubberItem)


class CmdMovePreviewRubberBase(QUndoCommand, Generic[TRubber]):
    _scene   : DiagramScene
    _rubber  : TRubber

    @checked(always=True)
    def __init__(
        self   : Self,
        scene  : DiagramScene,
        rubber : TRubber
    ) -> None:
        super().__init__()
        self._scene  = scene
        self._rubber = rubber

    def rubber(self : Self) -> TRubber:
        return self._rubber


class CmdMovePreviewRubberTee(CmdMovePreviewRubberBase[RubberTeeItem]):
    _segment : SegmentItem

    @checked(always=True)
    def __init__(self : Self, segment : SegmentItem, node : NodeItem) -> None:
        from .. import DiagramScene
        if not isinstance(scene := segment.scene(), DiagramScene):
            logger().error("Bad scene")
            self.setObsolete(True)
            return
        super().__init__(scene, RubberTeeItem(segment, node))
        self._segment = segment

    @checked
    def redo(self : Self) -> None:
        self._scene.addItem(self._rubber)
        self._scene.removeItem(self._segment)

    @checked
    def undo(self : Self) -> None:
        self._scene.addItem(self._segment)
        self._scene.removeItem(self._rubber)


class CmdMovePreviewRubberCorner(CmdMovePreviewRubberBase[RubberCornerItem]):
    _segment1 : SegmentItem
    _segment2 : SegmentItem
    _corner   : FreeNodeItem

    @checked(always=True)
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
        from .. import DiagramScene
        if not isinstance(scene := segment1.scene(), DiagramScene):
            logger().error("Bad scene")
            self.setObsolete(True)
            return
        super().__init__(scene, RubberCornerItem(segment1, segment2, node))
        self._segment1 = segment1
        self._segment2 = segment2
        if not isinstance(corner := segment1.otherNode(node), FreeNodeItem):
            logger().error("Bad corner")
            self.setObsolete(True)
            return
        self._corner = corner

    @checked
    def redo(self : Self) -> None:
        self._scene.addItem(self._rubber)
        self._scene.removeItem(self._segment1)
        self._scene.removeItem(self._segment2)
        self._scene.removeItem(self._corner)

    @checked
    def undo(self : Self) -> None:
        self._scene.addItem(self._corner)
        self._scene.addItem(self._segment1)
        self._scene.addItem(self._segment2)
        self._scene.removeItem(self._rubber)


class CmdMovePreviewRubberJog(CmdMovePreviewRubberBase[RubberJogItem]):
    _segment_or_static : SegmentItem | NodeItem

    @checked(always=True)
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
        from .. import DiagramScene
        if not isinstance(scene := mobile.scene(), DiagramScene):
            logger().error("Bad scene")
            self.setObsolete(True)
            return
        super().__init__(scene, RubberJogItem(segment_or_static, mobile, axis))
        self._segment_or_static = segment_or_static

    @checked
    def redo(self : Self) -> None:
        self._scene.addItem(self._rubber)
        if self._segment_or_static is not None:
            self._scene.removeItem(self._segment_or_static)

    @checked
    def undo(self : Self) -> None:
        if self._segment_or_static is not None:
            self._scene.addItem(self._segment_or_static)
        self._scene.removeItem(self._rubber)
