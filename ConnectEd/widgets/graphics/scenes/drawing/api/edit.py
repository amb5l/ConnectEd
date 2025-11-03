from PyQt6.QtCore import QPointF

from ......app import logger

from ......core.xml import copy

from .....dialogs.properties import PropertyState

from ....items               import ItemType, EdgeLoc, \
                                    SignalDirection, VectorRange, \
                                    QuillPrefChange, AppearancePrefChange

from ....items.block         import Block
from ....items.port_pin      import PortPinMixin
from ....items.block_pin     import BlockPin
from ....items.symbol_pin    import SymbolPin
from ....items.polyline      import Polyline, PolySeg
from ....items.base_text     import BaseText
from ....items.property_text import PropertyText
from ....items.anchor_point  import AnchorPoint
from ....items.mixin         import ItemMixin

from ..cmd           import cmdExec, CmdDelete, CmdMove
from ..cmd.block_pin import CmdMoveBlockPins
from ..cmd.edit      import CmdEditPortPin, \
                            CmdEditSymbolPinDot, CmdEditSymbolPinClock, \
                            CmdEditOrigin, \
                            CmdEditPolylineClosed, CmdEditPolySeg, \
                            CmdEditText, CmdEditPropertyText, \
                            CmdEditProperties, CmdEditAppearance


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


class DrawingSceneApiEditMixin:
    def editSelectArea(self : "DrawingScene") -> None:
        raise NotImplementedError("Not implemented yet")

    def editSelectAll(self : "DrawingScene") -> None:
        raise NotImplementedError("Not implemented yet")

    def editMove(
        self     : "DrawingScene",
        items    : list[ItemType],
        offset   : QPointF,
        slide    : bool = False,
        undoable : bool = False
    ) -> None:
        cmd = CmdMove(self, items, offset, slide)
        cmdExec(self, cmd, undoable)

    def editMoveBlockPins(
        self     : "DrawingScene",
        parent   : Block,
        pins     : list[BlockPin],
        after    : dict[BlockPin, EdgeLoc],
        before   : dict[BlockPin, EdgeLoc],
        undoable : bool = False
    ) -> None:
        cmd = CmdMoveBlockPins(parent, pins, after, before)
        cmdExec(self, cmd, undoable)

    def editCut(
        self     : "DrawingScene",
        pos      : QPointF = QPointF(0, 0),
        undoable : bool = False
    ) -> None:
        items = \
            [item for item in self.selectedItems() \
                if isinstance(item, ItemMixin) \
                and item.parentItem() is None]
        if items:
            copy(items, pos)
            cmd = CmdDelete(self, items)
            cmdExec(self, cmd, undoable)
        else:
            logger().warning("No items selected to cut")

    def editCopy(
        self     : "DrawingScene",
        pos      : QPointF = QPointF(0, 0)
    ) -> None:
        items = \
            [item for item in self.selectedItems() \
                if hasattr(item, "toXml") \
                and item.parentItem() is None]
        if items:
            copy(items, pos)
        else:
            logger().warning("No items selected to copy")

    def editDelete(
        self     : "DrawingScene",
        items    : list[ItemType] | None = None,
        undoable : bool = False
    ) -> None:
        """Delete selected items from the scene."""
        if items is None:
            items = self._selectedTopItems()
        if items:
            cmd = CmdDelete(self, items)
            cmdExec(self, cmd, undoable)
        else:
            logger().warning("No items selected to delete")

    def editPortPin(
        self      : "DrawingScene",
        item      : PortPinMixin,
        name      : str,
        direction : SignalDirection,
        range     : VectorRange,
        undoable  : bool = False
    ) -> None:
        cmd = CmdEditPortPin(self, item, name, direction, range)
        cmdExec(self, cmd, undoable)

    def editSymbolPinDot(
        self     : "DrawingScene",
        item     : SymbolPin,
        enable   : bool,
        undoable : bool = False
    ) -> None:
        cmd = CmdEditSymbolPinDot(self, item, enable)
        cmdExec(self, cmd, undoable)

    def editSymbolPinClock(
        self     : "DrawingScene",
        item     : SymbolPin,
        enable   : bool,
        undoable : bool = False
    ) -> None:
        cmd = CmdEditSymbolPinClock(self, item, enable)
        cmdExec(self, cmd, undoable)

    def editAssignOrigin(
        self     : "DrawingScene",
        ap       : AnchorPoint,
        undoable : bool = False
    ) -> None:
        cmd = CmdEditOrigin(self, ap)
        cmdExec(self, cmd, undoable)

    def editPolylineClosed(
        self     : "DrawingScene",
        polyline : Polyline,
        closed   : bool,
        sweep    : float | None,
        undoable : bool = False
    ) -> None:
        cmd = CmdEditPolylineClosed(self, polyline, closed, sweep)
        cmdExec(self, cmd, undoable)

    def editPolySeg(
        self     : "DrawingScene",
        seg      : PolySeg,
        sweep    : float | None,
        undoable : bool = False
    ) -> None:
        cmd = CmdEditPolySeg(self, seg, sweep)
        cmdExec(self, cmd, undoable)

    def editText(
        self       : "DrawingScene",
        item       : BaseText,
        text       : str,
        appearance : QuillPrefChange,
        undoable   : bool = False
    ) -> None:
        cmd = CmdEditText(self, item, text, appearance)
        cmdExec(self, cmd, undoable)

    def editPropertyText(
        self       : "DrawingScene",
        item       : PropertyText,
        name       : str,
        value      : str,
        appearance : QuillPrefChange,
        undoable   : bool = False
    ) -> None:
        cmd = CmdEditPropertyText(self, item, name, value, appearance)
        cmdExec(self, cmd, undoable)

    def editAppearance(
        self     : "DrawingScene",
        items    : list[ItemMixin],
        changes  : AppearancePrefChange,
        undoable : bool = False
    ) -> None:
        cmd = CmdEditAppearance(self, items, changes)
        cmdExec(self, cmd, undoable)

    def editProperties(
        self     : "DrawingScene",
        item     : ItemMixin,
        changes  : dict[str, PropertyState],
        undoable : bool = False
    ) -> None:
        cmd = CmdEditProperties(self, item, changes)
        cmdExec(self, cmd, undoable)

