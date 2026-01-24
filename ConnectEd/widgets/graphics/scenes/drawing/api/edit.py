from typing import Any

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui  import QColor

from ......app import logger

from ......core.xml import copy

from ....property   import PropertyEdit
from ....properties import PropertiesMixin

from ....items import ItemType, Default, NoChange, NO_CHANGE, AlignH, AlignV, \
                      EdgeLoc, SignalDirection

from ....items.block         import BlockItem
from ....items.port_pin      import PortPinMixin
from ....items.block_pin     import BlockPinItem
from ....items.symbol_pin    import SymbolPinItem
from ....items.polyline      import PolylineItem, PolySegItem
from ....items.text          import TextItem
from ....items.property_text import PropertyTextItem
from ....items.mixin         import ItemMixin

from ..cmd import cmdExec, CmdDelete, CmdMove, CmdRotateCW, CmdRotateCCW

from ..cmd.block_pin import CmdMoveBlockPins

from ..cmd.edit.pin           import CmdEditPortPin, \
                                     CmdEditSymbolPinDot, CmdEditSymbolPinClock
from ..cmd.edit.origin        import CmdEditOrigin
from ..cmd.edit.polyline      import CmdEditPolylineClosed, CmdEditPolySeg
from ..cmd.edit.text          import CmdEditText
from ..cmd.edit.property_text import CmdEditPropertyText
from ..cmd.edit.appearance    import CmdEditAppearance
from ..cmd.edit.properties    import CmdEditProperties

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
        parent   : BlockItem,
        pins     : list[BlockPinItem],
        after    : dict[BlockPinItem, EdgeLoc],
        before   : dict[BlockPinItem, EdgeLoc],
        undoable : bool = False
    ) -> None:
        cmd = CmdMoveBlockPins(parent, pins, after, before)
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

    def editText(
        self       : "DrawingScene",
        item       : TextItem,
        text       : str              | NoChange = NO_CHANGE,
        color      : QColor | Default | NoChange = NO_CHANGE,
        font       : str    | Default | NoChange = NO_CHANGE,
        size       : float  | Default | NoChange = NO_CHANGE,
        bold       : bool   | Default | NoChange = NO_CHANGE,
        italic     : bool   | Default | NoChange = NO_CHANGE,
        underline  : bool   | Default | NoChange = NO_CHANGE,
        align_h    : AlignH           | NoChange = NO_CHANGE,
        align_v    : AlignV           | NoChange = NO_CHANGE,
        width      : float | None     | NoChange = NO_CHANGE,
        height     : float | None     | NoChange = NO_CHANGE,
        anchor     : str              | NoChange = NO_CHANGE,
        undoable   : bool = False
    ) -> None:
        cmd = CmdEditText(
            self, item, text, align_h, align_v, width, height,
            color, font, size, bold, italic, underline

        )
        cmdExec(self, cmd, undoable)

    def editPropertyText(
        self       : "DrawingScene",
        item       : PropertyTextItem,
        value      : str,
        color      : QColor | Default | NoChange = NO_CHANGE,
        font       : str    | Default | NoChange = NO_CHANGE,
        size       : float  | Default | NoChange = NO_CHANGE,
        bold       : bool   | Default | NoChange = NO_CHANGE,
        italic     : bool   | Default | NoChange = NO_CHANGE,
        underline  : bool   | Default | NoChange = NO_CHANGE,
        undoable   : bool = False
    ) -> None:
        cmd = CmdEditPropertyText(
            self, item, value, color, font, size, bold, italic, underline
        )
        cmdExec(self, cmd, undoable)

    def editAppearance(
        self           : "DrawingScene",
        items          : list[ItemMixin],
        line_color     : QColor        | Default | NoChange = NO_CHANGE,
        line_width     : float         | Default | NoChange = NO_CHANGE,
        line_style     : Qt.PenStyle   | Default | NoChange = NO_CHANGE,
        fill_color     : QColor        | Default | NoChange = NO_CHANGE,
        fill_style     : Qt.BrushStyle | Default | NoChange = NO_CHANGE,
        text_color     : QColor        | Default | NoChange = NO_CHANGE,
        text_family    : str           | Default | NoChange = NO_CHANGE,
        text_size      : float         | Default | NoChange = NO_CHANGE,
        text_bold      : bool          | Default | NoChange = NO_CHANGE,
        text_italic    : bool          | Default | NoChange = NO_CHANGE,
        text_underline : bool          | Default | NoChange = NO_CHANGE,
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

    def editProperties(
        self     : "DrawingScene",
        object   : PropertiesMixin,
        changes  : PropertyEdit,
        undoable : bool = False
    ) -> None:
        cmd = CmdEditProperties(object, changes)
        cmdExec(self, cmd, undoable)
