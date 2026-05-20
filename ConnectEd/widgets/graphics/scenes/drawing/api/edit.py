from PyQt6.QtCore import Qt
from PyQt6.QtCore import QPointF
from PyQt6.QtGui  import QColor

from ......app import logger
from ......core.check import checked
from ......core.types import NoChange, NO_CHANGE, \
                             AlignH, AlignV, Direction, RectHandleId
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
        items    : ItemType | list[ItemType],
        offset   : QPointF,
        slide    : bool = False,
        undoable : bool = False
    ) -> None:
        if not isinstance(items, list):
            items = [items]
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
        text      : str           | NoChange = NO_CHANGE,
        block     : bool          | NoChange = NO_CHANGE,
        rotation  : float         | NoChange = NO_CHANGE,
        autoflip  : bool          | NoChange = NO_CHANGE,
        mirror_h  : bool          | NoChange = NO_CHANGE,
        mirror_v  : bool          | NoChange = NO_CHANGE,
        origin    : RectHandleId  | NoChange = NO_CHANGE,
        align_h   : AlignH        | NoChange = NO_CHANGE,
        align_v   : AlignV        | NoChange = NO_CHANGE,
        width     : float         | NoChange = NO_CHANGE,
        height    : float         | NoChange = NO_CHANGE,
        color     : QColor | None | NoChange = NO_CHANGE,
        font      : str    | None | NoChange = NO_CHANGE,
        size      : float  | None | NoChange = NO_CHANGE,
        bold      : bool   | None | NoChange = NO_CHANGE,
        italic    : bool   | None | NoChange = NO_CHANGE,
        underline : bool   | None | NoChange = NO_CHANGE,
        undoable  : bool                    = False
    ) -> None:
        cmd = CmdEditText(
            self, item, text, block,
            rotation, mirror_h, mirror_v, autoflip,
            origin, align_h, align_v, width, height,
            color, font, size, bold, italic, underline
        )
        cmdExec(self, cmd, undoable)

    def editAppearance(
        self           : "DrawingScene",
        items          : list[ItemMixin],
        line_color     : QColor        | None | NoChange = NO_CHANGE,
        line_width     : float         | None | NoChange = NO_CHANGE,
        line_style     : Qt.PenStyle   | None | NoChange = NO_CHANGE,
        fill_color     : QColor        | None | NoChange = NO_CHANGE,
        fill_style     : Qt.BrushStyle | None | NoChange = NO_CHANGE,
        text_color     : QColor        | None | NoChange = NO_CHANGE,
        text_font      : str           | None | NoChange = NO_CHANGE,
        text_size      : float         | None | NoChange = NO_CHANGE,
        text_bold      : bool          | None | NoChange = NO_CHANGE,
        text_italic    : bool          | None | NoChange = NO_CHANGE,
        text_underline : bool          | None | NoChange = NO_CHANGE,
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
            text_font,
            text_size,
            text_bold,
            text_italic,
            text_underline
        )
        cmdExec(self, cmd, undoable)
