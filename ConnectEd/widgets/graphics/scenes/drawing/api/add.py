from typing import Self

from PyQt6.QtCore import QPointF

from ......core.check import checked

from ....items import ItemType

from ....items.polyline  import PolylineItem, PolyVtxItem

from ..cmd          import cmdExec, CmdAdd
from ..cmd.polyline import CmdAddPolyVtx

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene
    MixinSelf = Self | DrawingScene


class DrawingSceneApiAddMixin:
    """Methods to add items to the scene."""

    @checked
    def addItems(
        self     : "MixinSelf",
        items    : list[ItemType],
        undoable : bool = False
    ) -> None:
        """Add an item to the scene. TODO support single item."""
        cmd = CmdAdd(self, items)
        cmdExec(self, cmd, undoable)

    @checked
    def addPolyVtx(
        self     : "MixinSelf",
        polyline : PolylineItem,
        pos      : QPointF,
        sweep    : float | None = None,
        undoable : bool = False
    ) -> PolyVtxItem:
        """Add a vertex to a polyline."""
        cmd = CmdAddPolyVtx(polyline, pos, sweep)
        cmdExec(self, cmd, undoable)
        return cmd.vtx()
