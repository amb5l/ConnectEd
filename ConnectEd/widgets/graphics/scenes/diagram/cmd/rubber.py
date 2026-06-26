from __future__ import annotations

from typing import Self

from PyQt6.QtGui import QUndoCommand

from ......core.types   import Axis

from ....items.node    import NodeItem, FreeNodeItem
from ....items.segment import SegmentItem
from ....items.rubber  import RubberItem, \
                              RubberTeeItem, RubberCornerItem, RubberJogItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....scenes.diagram import DiagramScene


class CmdMovePreviewRubberBase(QUndoCommand):
    _scene   : DiagramScene
    _rubber  : RubberItem

    def __init__(
        self   : Self,
        scene  : DiagramScene,
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
