from PyQt6.QtCore import QPointF

from ......app import logger
from ......core.check import checked
from ......core.types import NoChange, NO_CHANGE, \
                             AlignH, AlignV, Direction, RectHandleId, \
                             Color, PenWidth, PenStyle, BrushStyle, \
                             FontFamily, FontSize, FontBool
from ......core.xml    import copy

from ....items import ItemType

from ....items.port_pin      import PortPinMixin
from ....items.symbol_pin    import SymbolPinItem
from ....items.polyline      import PolylineItem, PolySegItem
from ....items.text          import TextItem
from ....items.mixin         import ItemMixin

from ..cmd import cmdExec, CmdDelete, CmdMove, CmdRotateCW, CmdRotateCCW

from ..cmd.edit.pin           import CmdEditPortPin, \
                                     CmdEditSymbolPinDot, CmdEditSymbolPinClock
from ..cmd.edit.origin        import CmdEditOrigin
from ..cmd.edit.polyline      import CmdEditPolylineClosed, CmdEditPolySeg
from ..cmd.edit.text          import CmdEditText
from ..cmd.edit.appearance    import CmdEditAppearance

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

    def editRotateCW(
        self     : "DrawingScene",
        items    : list[ItemType],
        pos      : QPointF | None = None,  # individual if None, group otherwise
        undoable : bool = False
    ) -> None:
        cmd = CmdRotateCW(self, items, pos)
        cmdExec(self, cmd, undoable)

    def editRotateCCW(
        self     : "DrawingScene",
        items    : list[ItemType],
        pos      : QPointF | None = None,  # individual if None, group otherwise
        undoable : bool = False
    ) -> None:
        cmd = CmdRotateCCW(self, items, pos)
        cmdExec(self, cmd, undoable)

    def editCut(
        self     : "DrawingScene",
        pos      : QPointF | None = None,  # None => QPointF(0, 0)
        undoable : bool = False
    ) -> None:
        pos = pos or QPointF(0, 0)
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
        self : "DrawingScene",
        pos  : QPointF | None = None
    ) -> None:
        pos = pos or QPointF(0, 0)
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
        """
        Delete selected items from the scene.
        TODO: make property texts invisible, otherwise skip items with parents.
        """
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
        direction : Direction,
        undoable  : bool = False
    ) -> None:
        cmd = CmdEditPortPin(self, item, name, direction)
        cmdExec(self, cmd, undoable)

    def editSymbolPinDot(
        self     : "DrawingScene",
        item     : SymbolPinItem,
        enable   : bool,
        undoable : bool = False
    ) -> None:
        cmd = CmdEditSymbolPinDot(self, item, enable)
        cmdExec(self, cmd, undoable)

    def editSymbolPinClock(
        self     : "DrawingScene",
        item     : SymbolPinItem,
        enable   : bool,
        undoable : bool = False
    ) -> None:
        cmd = CmdEditSymbolPinClock(self, item, enable)
        cmdExec(self, cmd, undoable)

    def editAssignOrigin(
        self     : "DrawingScene",
        item     : "ItemMixin",
        ap_name  : str,
        undoable : bool = False
    ) -> None:
        cmd = CmdEditOrigin(self, item, ap_name)
        cmdExec(self, cmd, undoable)

    def editPolylineClosed(
        self     : "DrawingScene",
        polyline : PolylineItem,
        closed   : bool,
        sweep    : float | None,
        undoable : bool = False
    ) -> None:
        cmd = CmdEditPolylineClosed(self, polyline, closed, sweep)
        cmdExec(self, cmd, undoable)

    def editPolySeg(
        self     : "DrawingScene",
        seg      : PolySegItem,
        sweep    : float | None,
        undoable : bool = False
    ) -> None:
        cmd = CmdEditPolySeg(self, seg, sweep)
        cmdExec(self, cmd, undoable)

    @checked
    def editText(
        self      : "DrawingScene",
        item      : TextItem,
        text      : str          | NoChange = NO_CHANGE,
        block     : bool         | NoChange = NO_CHANGE,
        rotation  : float        | NoChange = NO_CHANGE,
        flip      : bool         | NoChange = NO_CHANGE,
        origin    : RectHandleId | NoChange = NO_CHANGE,
        align_h   : AlignH       | NoChange = NO_CHANGE,
        align_v   : AlignV       | NoChange = NO_CHANGE,
        width     : float        | NoChange = NO_CHANGE,
        height    : float        | NoChange = NO_CHANGE,
        color     : Color        | NoChange = NO_CHANGE,
        family    : FontFamily   | NoChange = NO_CHANGE,
        size      : FontSize     | NoChange = NO_CHANGE,
        bold      : FontBool     | NoChange = NO_CHANGE,
        italic    : FontBool     | NoChange = NO_CHANGE,
        underline : FontBool     | NoChange = NO_CHANGE,
        undoable  : bool                    = False
    ) -> None:
        cmd = CmdEditText(
            self, item, text, block,
            rotation, flip,  origin, align_h, align_v, width, height,
            color, family, size, bold, italic, underline
        )
        cmdExec(self, cmd, undoable)

    def editAppearance(
        self           : "DrawingScene",
        items          : list[ItemMixin],
        line_color     : Color      | NoChange = NO_CHANGE,
        line_width     : PenWidth   | NoChange = NO_CHANGE,
        line_style     : PenStyle   | NoChange = NO_CHANGE,
        fill_color     : Color      | NoChange = NO_CHANGE,
        fill_style     : BrushStyle | NoChange = NO_CHANGE,
        text_color     : Color      | NoChange = NO_CHANGE,
        text_family    : FontFamily | NoChange = NO_CHANGE,
        text_size      : FontSize   | NoChange = NO_CHANGE,
        text_bold      : FontBool   | NoChange = NO_CHANGE,
        text_italic    : FontBool   | NoChange = NO_CHANGE,
        text_underline : FontBool   | NoChange = NO_CHANGE,
        undoable       : bool = False
    ) -> None:
        cmd = CmdEditAppearance(
            self,
            items,
            line_color,
            line_width,
            line_style,
            fill_color,
            fill_style,
            text_color,
            text_family,
            text_size,
            text_bold,
            text_italic,
            text_underline
        )
        cmdExec(self, cmd, undoable)
