from typing import Any

from PyQt6.QtCore import QPointF
from PyQt6.QtGui  import QColor

from ....properties import PropertyDisplay, PropertiesMixin

from ....items import ItemType, Default, AlignH, AlignV

from ....items.block     import BlockItem
from ....items.block_pin import BlockPinItem
from ....items.polyline  import PolylineItem, PolyVtxItem

from ..cmd                 import cmdExec, CmdAdd
from ..cmd.block_pin       import CmdAddBlockPin
from ..cmd.polyline        import CmdAddPolyVtx
from ..cmd.edit.properties import CmdAddProperty

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....properties import PropertiesMixin
    from .. import DrawingScene


class DrawingSceneApiAddMixin:
    """Methods to add items to the scene."""

    def addItems(
        self     : "DrawingScene",
        items    : list[ItemType],
        undoable : bool = False
    ) -> None:
        """Add an item to the scene."""
        cmd = CmdAdd(self, items)
        cmdExec(self, cmd, undoable)

    def addBlockPin(
        self     : "DrawingScene",
        parent   : BlockItem,
        pin      : BlockPinItem,
        undoable : bool = False
    ) -> BlockPinItem:
        """Add a block pin to the scene."""
        cmd = CmdAddBlockPin(parent, pin)
        cmdExec(self, cmd, undoable)
        return cmd.pin()

    def addPolyline(
        self     : "DrawingScene",
        vertices : list[QPointF],
        closed   : bool = False,
        undoable : bool = False
    ) -> PolylineItem:
        """Add a polyline to the scene."""
        item = PolylineItem(vertices, closed)
        self.addItems([item], undoable)
        return item

    def addPolyVtx(
        self     : "DrawingScene",
        polyline : PolylineItem,
        pos      : QPointF,
        sweep    : float | None = None,
        undoable : bool = False
    ) -> PolyVtxItem:
        """Add a vertex to a polyline."""
        cmd = CmdAddPolyVtx(polyline, pos, sweep)
        cmdExec(self, cmd, undoable)
        return cmd.vtx()

    def addProperty(
        self      : "DrawingScene",
        object    : "PropertiesMixin",
        name      : str,
        value     : Any,
        display   : PropertyDisplay        = PropertyDisplay.NONE,
        cleat     : str              | None = None,
        x         : float            | None = None,
        y         : float            | None = None,
        origin    : str              | None = None,
        align_h   : AlignH           | None = None,
        align_v   : AlignV           | None = None,
        width     : float            | None = None,
        height    : float            | None = None,
        color     : QColor | Default | None = None,
        family    : str    | Default | None = None,
        size      : float  | Default | None = None,
        bold      : bool   | Default | None = None,
        italic    : bool   | Default | None = None,
        underline : bool   | Default | None = None,
        undoable  : bool                    = False
    ) -> None:
        """Add a property to the scene."""
        cmd = CmdAddProperty(object, name)
        cmdExec(self, cmd, undoable)
