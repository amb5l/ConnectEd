from __future__ import annotations

from typing          import Self, cast
from collections.abc import Sequence

from PyQt6.QtCore    import Qt, QPointF, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QColor

from ......app import logger

from ......core.check import checked
from ......core.types import NoChange, NO_CHANGE, AlignH, AlignV, \
                             EdgeLoc, Direction, HandleId, RectHandleId
from ......core.xml   import XmlProtocol

from ....items.grip          import GripItem
from ....items.polyline      import PolylineItem, PolySegItem
from ....items.text          import TextItem
from ....items.port_pin      import PortPinMixin, PortPinPathItem
from ....items.block_pin     import BlockPinItem
from ....items.symbol_pin    import SymbolPinItem
from ....items.block         import BlockItem
from ....items.symbol        import SymbolInstanceItem
from ....items.property_text import PropertyTextItem
from ....items.segment       import SegmentItem

from ....items.mixin import ItemMixin

from ....items.mixin.move      import ItemMoveMixin
from ....items.mixin.transform import ItemTransformMixin

from ..cmd import cmdExec, CmdMove, CmdMoveGrip, CmdRotateCW, CmdRotateCCW, \
                  CmdDelete

from ..cmd.edit.pin        import CmdEditPortPin, \
                                  CmdEditPinDot, CmdEditPinClk
from ..cmd.edit.origin     import CmdEditOrigin
from ..cmd.edit.polyline   import CmdEditPolylineClosed, CmdEditPolySeg
from ..cmd.edit.text       import CmdEditText
from ..cmd.edit.appearance import CmdEditAppearance

from ..cmd.block_pin import CmdMoveBlockPins

from ..xml import diagram_scene_xml_items

from ..host import asDiagramScene


class DiagramSceneApiEditMixin:

    @checked
    def editSelectArea(self : Self) -> None:
        raise NotImplementedError("Not implemented yet")

    @checked
    def editSelectAll(self : Self) -> None:
        raise NotImplementedError("Not implemented yet")

    @checked
    def editMove(
        self     : Self,
        items    : QGraphicsItem | list[QGraphicsItem],
        offset   : QPointF,
        slide    : bool = False,
        undoable : bool = False
    ) -> None:
        host = asDiagramScene(self)
        if not isinstance(items, list):
            items = [items]
        filtered_items : list[QGraphicsItem] = [
            item for item in items
            if isinstance(item, ItemMixin)
            and isinstance(item, ItemMoveMixin)
            and item.movable()
            and item.topParentItem() not in items
        ]
        cmd = CmdMove(host, filtered_items, offset)
        cmdExec(host, cmd, undoable)

    @checked
    def editMoveGrip(
        self     : Self,
        grip     : GripItem,
        offset   : QPointF,
        undoable : bool = False
    ) -> None:
        host = asDiagramScene(self)
        if not grip.movable() or offset == QPointF(0, 0):
            return
        cmd = CmdMoveGrip(host, grip, offset)
        cmdExec(host, cmd, undoable)

    @checked
    def editRotateCW(
        self     : Self,
        items    : QGraphicsItem | list[QGraphicsItem],
        pos      : QPointF | None = None,  # individual if None, group otherwise
        undoable : bool = False
    ) -> None:
        host = asDiagramScene(self)
        if not isinstance(items, list):
            items = [items]
        cmd = CmdRotateCW(host, items, pos)
        cmdExec(host, cmd, undoable)

    @checked
    def editRotateCCW(
        self     : Self,
        items    : QGraphicsItem | list[QGraphicsItem],
        pos      : QPointF | None = None,  # individual if None, group otherwise
        undoable : bool = False
    ) -> None:
        host = asDiagramScene(self)
        if not isinstance(items, list):
            items = [items]
        cmd = CmdRotateCCW(host, items, pos)
        cmdExec(host, cmd, undoable)

    @checked
    def editCut(
        self     : Self,
        pos      : QPointF | None = None,  # None => QPointF(0, 0)
        undoable : bool = False
    ) -> None:
        host = asDiagramScene(self)
        pos = pos or QPointF(0, 0)
        items = host._selectedTopItems()
        if items:
            host.copy(items, pos)
            cmd = CmdDelete(host, cast(list[QGraphicsItem], items))
            cmdExec(host, cmd, undoable)
        else:
            logger().warning("No items selected to cut")

    @checked
    def editCopy(
        self : Self,
        pos  : QPointF | None = None
    ) -> None:
        host = asDiagramScene(self)
        pos = pos or QPointF(0, 0)
        items = host._selectedTopItems()
        if items:
            host.copy(items, pos)
        else:
            logger().warning("No items selected to copy")

    @checked
    def editPaste(
        self     : Self,
        pos      : QPointF | None = None,
        undoable : bool = False
    ) -> None:
        host = asDiagramScene(self)
        pos = pos or QPointF(0, 0)

        def fromXmlItem(
            xr       : QXmlStreamReader,
            undoable : bool,
            item_cls : type[XmlProtocol]
        ) -> None:
            if item_cls == SegmentItem:
                attrs = xr.attributes()
                x1 = attrs.value("X1")
                if x1:
                    p1 = QPointF(float(x1), float(attrs.value("Y1")))
                    p2 = QPointF(float(attrs.value("X2")), float(attrs.value("Y2")))
                    host.addSegment(p1, p2, undoable=undoable)
                else:
                    logger().warning("Segment missing X1/Y1/X2/Y2 attributes")
            else:
                if not isinstance(item := item_cls.fromXml(xr), QGraphicsItem):
                    raise TypeError("Bad item")
                host.addItems(item, undoable)
                if isinstance(item, SymbolInstanceItem):
                    name = item.name()
                    definition = host._symbols.get(name, None)
                    if definition:
                        item.syncFromDefinition(definition)
                    else:
                        logger().warning(f"Symbol {name} not found")

        xref = {}
        for item_name, item_cls in diagram_scene_xml_items.items():
            xref[item_name] = \
                lambda xr, undoable, cls=item_cls: \
                    (fromXmlItem(xr, undoable, cls), None)[1]
        items, src_pos = host.paste()
        src_pos = src_pos or QPointF(0, 0)

    @checked
    def editDelete(
        self     : Self,
        items    : QGraphicsItem | Sequence[QGraphicsItem] | None = None,
        undoable : bool = False
    ) -> None:
        """Delete selected items from the scene; netlist aware."""
        host = asDiagramScene(self)
        if items is None:
            items = host._selectedTopItems()
        elif isinstance(items, QGraphicsItem):
            items = [items]
        else:
            items = list(items)
        # filter out items with parents apart from property texts
        for item in items:
            if item.parentItem() is not None:
                if isinstance(item, PropertyTextItem):
                    continue
                items.remove(item)
        # check that there is something to do
        if items == []:
            logger().warning("No items to delete")
            return
        # start macro
        if undoable:
            host.undo_stack.beginMacro("editDelete")
        # remove segments (netlist aware)
        for item in items[:]:
            if isinstance(item, SegmentItem):
                host.removeSegment(item, undoable)
                items.remove(item)
        # delete remaining items
        if items:
            cmd = CmdDelete(host, items)
            cmdExec(host, cmd, undoable)
        # end macro
        if undoable:
            host.undo_stack.endMacro()

    @checked
    def editPortPin(
        self      : Self,
        item      : PortPinMixin,
        name      : str,
        direction : Direction,
        undoable  : bool = False
    ) -> None:
        host = asDiagramScene(self)
        cmd = CmdEditPortPin(host, item, name, direction)
        cmdExec(host, cmd, undoable)

    @checked
    def editPinDot(
        self     : Self,
        item     : PortPinPathItem,
        enable   : bool,
        undoable : bool = False
    ) -> None:
        host = asDiagramScene(self)
        cmd = CmdEditPinDot(host, item, enable)
        cmdExec(host, cmd, undoable)

    @checked
    def editPinClk(
        self     : Self,
        item     : SymbolPinItem,
        enable   : bool,
        undoable : bool = False
    ) -> None:
        host = asDiagramScene(self)
        cmd = CmdEditPinClk(host, item, enable)
        cmdExec(host, cmd, undoable)

    @checked
    def editAssignOrigin(
        self     : Self,
        item     : QGraphicsItem,
        handle   : HandleId,
        undoable : bool = False
    ) -> None:
        host = asDiagramScene(self)
        if not isinstance(item, ItemTransformMixin):
            raise TypeError("Bad item")
        cmd = CmdEditOrigin(host, item, handle)
        cmdExec(host, cmd, undoable)

    @checked
    def editPolylineClosed(
        self     : Self,
        polyline : PolylineItem,
        closed   : bool,
        sweep    : float | None,
        undoable : bool = False
    ) -> None:
        host = asDiagramScene(self)
        cmd = CmdEditPolylineClosed(host, polyline, closed, sweep)
        cmdExec(host, cmd, undoable)

    @checked
    def editPolySeg(
        self     : Self,
        seg      : PolySegItem,
        sweep    : float | None,
        undoable : bool = False
    ) -> None:
        host = asDiagramScene(self)
        cmd = CmdEditPolySeg(host, seg, sweep)
        cmdExec(host, cmd, undoable)

    @checked
    def editText(
        self       : Self,
        item       : TextItem,
        text       : str          | NoChange = NO_CHANGE,
        block      : bool         | NoChange = NO_CHANGE,
        rotation   : float        | NoChange = NO_CHANGE,
        autoflip   : bool         | NoChange = NO_CHANGE,
        mirror_h   : bool         | NoChange = NO_CHANGE,
        mirror_v   : bool         | NoChange = NO_CHANGE,
        origin     : RectHandleId | NoChange = NO_CHANGE,
        align_h    : AlignH       | NoChange = NO_CHANGE,
        align_v    : AlignV       | NoChange = NO_CHANGE,
        width      : float        | NoChange = NO_CHANGE,
        height     : float        | NoChange = NO_CHANGE,
        pad_left   : float        | NoChange = NO_CHANGE,
        pad_right  : float        | NoChange = NO_CHANGE,
        pad_top    : float        | NoChange = NO_CHANGE,
        pad_bottom : float        | NoChange = NO_CHANGE,
        color      : QColor       | None | NoChange = NO_CHANGE,
        font       : str          | None | NoChange = NO_CHANGE,
        size       : float        | None | NoChange = NO_CHANGE,
        bold       : bool         | None | NoChange = NO_CHANGE,
        italic     : bool         | None | NoChange = NO_CHANGE,
        underline  : bool         | None | NoChange = NO_CHANGE,
        undoable   : bool                    = False
    ) -> None:
        host = asDiagramScene(self)
        cmd = CmdEditText(
            host, item, text, block,
            rotation, mirror_h, mirror_v, autoflip,
            origin, align_h, align_v, width, height,
            pad_left, pad_right, pad_top, pad_bottom,
            color, font, size, bold, italic, underline
        )
        cmdExec(host, cmd, undoable)

    @checked
    def editAppearance(
        self           : Self,
        items          : QGraphicsItem | list[QGraphicsItem],
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
        host = asDiagramScene(self)
        cmd = CmdEditAppearance(
            host,
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
        cmdExec(host, cmd, undoable)

    @checked
    def editMoveBlockPins(
        self     : Self,
        parent   : BlockItem,
        pins     : list[BlockPinItem],
        after    : dict[BlockPinItem, EdgeLoc],
        before   : dict[BlockPinItem, EdgeLoc],
        undoable : bool = False
    ) -> None:
        host = asDiagramScene(self)
        cmd = CmdMoveBlockPins(parent, pins, after, before)
        cmdExec(host, cmd, undoable)
