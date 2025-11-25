from typing import Self
from dataclasses import dataclass

from PyQt6.QtCore import QPointF

from .....dialogs.properties import DisplayChoice, \
                                    PropertyVariables, PropertyChange

from ....properties import PropertiesMixin

from ....items import SignalDirection, VectorRange, \
                      QuillPref, QuillPrefChange, \
                      AppearancePref, AppearancePrefChange

from ....items.mixin        import ItemMixin
from ....items.mixin.origin import ItemOriginMixin

from ....items.polyline      import Polyline, PolySeg
from ....items.base_text     import BaseTextMixin
from ....items.property_text import PropertyTextMixin, \
                                    PropertyTextBlock, PropertyTextLine

from . import CmdBase, CmdSceneItem, CmdSceneItems

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....scenes.drawing   import DrawingScene
    from ....items.port_pin   import PortPinMixin
    from ....items.symbol_pin import SymbolPin


class CmdEditPortPin(CmdSceneItem):
    @dataclass
    class PortPinState:
        name      : str
        direction : SignalDirection
        range     : VectorRange

    _item   : "PortPinMixin"
    _before : PortPinState
    _after  : PortPinState

    def __init__(
        self      : Self,
        scene     : "DrawingScene",
        item      : "PortPinMixin",
        name      : str,
        direction : SignalDirection,
        range     : VectorRange
    ):
        super().__init__(scene, item)
        self._before = self.PortPinState(
            item.name(), item.direction(), item.range()
        )
        self._after  = self.PortPinState(name, direction, range)

    def redo(self : Self) -> None:
        self._item.setName(self._after.name)
        self._item.setDirection(self._after.direction)
        self._item.setRange(self._after.range)
        self._item.update()

    def undo(self : Self) -> None:
        self._item.setName(self._before.name)
        self._item.setDirection(self._before.direction)
        self._item.setRange(self._before.range)
        self._item.update()


class CmdEditSymbolPinDot(CmdSceneItem):
    _item   : "SymbolPin"
    _before : bool
    _after  : bool

    def __init__(
        self   : Self,
        scene  : "DrawingScene",
        item   : "SymbolPin",
        enable : bool
    ):
        super().__init__(scene, item)
        self._before = item.dot
        self._after = enable

    def redo(self : Self) -> None:
        self._item.dot = self._after
        self._item.update()

    def undo(self : Self) -> None:
        self._item.dot = self._before
        self._item.update()


class CmdEditSymbolPinClock(CmdSceneItem):
    _item   : "SymbolPin"
    _before : bool
    _after  : bool

    def __init__(
        self : Self,
        scene : "DrawingScene",
        item : "SymbolPin",
        enable : bool
    ):
        super().__init__(scene, item)
        self._before = item.clock
        self._after = enable

    def redo(self : Self) -> None:
        self._item.clock = self._after
        self._item.update()

    def undo(self : Self) -> None:
        self._item.clock = self._before
        self._item.update()


class CmdEditPolylineClosed(CmdSceneItem):
    _item   : Polyline
    _before : bool
    _after  : bool
    _sweep  : float | None

    def __init__(
        self   : Self,
        scene  : "DrawingScene",
        item   : Polyline,
        closed : bool,
        sweep  : float | None
    ):
        super().__init__(scene, item)
        self._item = item
        self._before = item.closed()
        self._after = closed
        self._sweep = sweep

    def redo(self : Self) -> None:
        if self._after:
            self._item.close(self._sweep)
        else:
            self._item.open()

    def undo(self : Self) -> None:
        if self._before:
            self._item.close(self._sweep)
        else:
            self._item.open()


class CmdEditPolySeg(CmdSceneItem):
    _item   : PolySeg
    _before : float | None
    _after  : float | None

    def __init__(
        self  : Self,
        scene : "DrawingScene",
        seg   : PolySeg,
        sweep : float | None
    ):
        super().__init__(scene, seg)
        self._before = seg.sweep()
        self._after = sweep

    def redo(self : Self) -> None:
        self._item.setSweep(self._after)
        parent : Polyline = self._item.parentItem()
        parent.updatePath()

    def undo(self : Self) -> None:
        self._item.setSweep(self._before)
        parent : Polyline = self._item.parentItem()
        parent.updatePath()


class CmdEditText(CmdSceneItem):
    @dataclass
    class TextState:
        text       : str
        appearance : QuillPref

    _item   : BaseTextMixin
    _before : TextState
    _after  : TextState

    def __init__(
        self       : Self,
        scene      : "DrawingScene",
        item       : BaseTextMixin,
        text       : str,
        appearance : QuillPrefChange
    ):
        super().__init__(scene, item)
        self._item   = item
        self._before = self.TextState(item.text(), item.a.quill.getPref())
        self._after  = self.TextState(text, appearance)

    def redo(self : Self) -> None:
        self._item.setText(self._after.text)
        self._item.a.quill.setPref(self._after.appearance)
        self._item.update()

    def undo(self : Self) -> None:
        self._item.setText(self._before.text)
        self._item.a.quill.setPref(self._before.appearance)
        self._item.update()


class CmdEditPropertyText(CmdSceneItem):
    @dataclass
    class PropertyTextState:
        value      : str
        appearance : QuillPref

    _item   : PropertyTextMixin
    _before : PropertyTextState
    _after  : PropertyTextState

    def __init__(
        self       : Self,
        scene      : "DrawingScene",
        item       : PropertyTextMixin,
        value      : str,
        appearance : QuillPrefChange
    ):
        super().__init__(scene, item)
        self._item           = item
        self._before = self.PropertyTextState(item.value(), item.a.quill.getPref())
        self._after  = self.PropertyTextState(value, appearance)

    def redo(self : Self) -> None:
        self._item.setValue(self._after.value)
        self._item.a.quill.setPref(self._after.appearance)
        self._item.update()

    def undo(self : Self) -> None:
        self._item.setValue(self._before.value)
        self._item.a.quill.setPref(self._before.appearance)
        self._item.update()


class CmdEditAppearance(CmdSceneItems):
    _before : dict[ItemMixin, AppearancePref]
    _after  : AppearancePrefChange

    def __init__(
        self    : Self,
        scene   : "DrawingScene",
        items   : list[ItemMixin],
        changes : AppearancePrefChange
    ):
        super().__init__(scene, items)
        self._after = changes
        self._before = {}
        for e in items:
            p = AppearancePref()
            p.line  = e.line.getPref()  if hasattr(e, "line")  else None
            p.fill  = e.fill.getPref()  if hasattr(e, "fill")  else None
            p.quill = e.quill.getPref() if hasattr(e, "quill") else None
            self._before[e] = p

    def redo(self : Self) -> None:
        c = self._after
        for e in self._items:
            if not hasattr(e, "a"):
                continue
            if e.a.line  is not None: e.a.line.setPref(c.line)
            if e.a.fill  is not None: e.a.fill.setPref(c.fill)
            if e.a.quill is not None: e.a.quill.setPref(c.quill)
            e.onGeometryChange()
            e.update()

    def undo(self : Self) -> None:
        for e in self._items:
            c = self._before[e]
            if not hasattr(e, "a"):
                continue
            if e.a.line  is not None: e.a.line.setPref(c.line)
            if e.a.fill  is not None: e.a.fill.setPref(c.fill)
            if e.a.quill is not None: e.a.quill.setPref(c.quill)
            e.onGeometryChange()
            e.update()


class CmdEditProperties(CmdBase):
    _object  : PropertiesMixin
    _changes : dict[str, PropertyChange]

    def __init__(
        self    : Self,
        object  : PropertiesMixin,
        changes : dict[str, PropertyChange]
    ):
        self._object  = object
        self._changes = changes
        super().__init__()

    def redo(self : Self) -> None:
        self._do("before", "after")

    def undo(self : Self) -> None:
        self._do("after", "before")

    def _do(self : Self, before_attr : str, after_attr : str) -> None:
        for _name, change in self._changes.items():
            before : PropertyVariables | None = getattr(change, before_attr)
            after  : PropertyVariables | None = getattr(change, after_attr)
            if before is None:
                # add property
                self._object.initProperty(after.name, after.value)
                if after.display != DisplayChoice.NONE:
                    self._addPropertyText(after)
            elif after is None:
                # delete property
                del self._object.properties[before.name]
            else:
                # existing property
                self._object.renProperty(before.name, after.name)
                self._object.properties[after.name].set(after.value)
                pt = self._object.properties[after.name].getText()
                if pt is None:
                    if after.display != DisplayChoice.NONE:
                        self._addPropertyText(after)
                else:
                    if after.display == DisplayChoice.NONE:
                        self._object.properties[after.name].setText(None)
                    else:
                        self._modifyPropertyText(pt, after)

    def _addPropertyText(self : Self, vars : PropertyVariables) -> None:
        block_classes = (DisplayChoice.BLOCK, DisplayChoice.BLOCK_HIDDEN)
        pt_class = PropertyTextBlock if vars.display in block_classes \
            else PropertyTextLine
        pt = pt_class()
        self._modifyPropertyText(pt, vars)
        parent =  self._object.getHandle(vars.cleat) if vars.cleat != "" else \
            self._object if isinstance(self._object, ItemMixin) else \
            None
        pt.setParentItem(parent)
        if parent is None:
            self._object.addItem(pt)  # add to scene
        self._object.properties[vars.name].setText(pt)
        pt.onTextChange()  # Refresh text after parenting

    def _modifyPropertyText(
        self : Self,
        pt   : PropertyTextMixin,
        vars : PropertyVariables
    ) -> None:
        pt.setName(vars.name)
        pt.setVisible(vars.display in (DisplayChoice.LINE, DisplayChoice.BLOCK))
        pt.setCleat(vars.cleat)
        pt.setPos(QPointF(vars.offset_x, vars.offset_y))
        pt.setOrigin(vars.origin)
        pt.a.quill.setFamily(vars.font)
        pt.a.quill.setSize(vars.size)
        pt.a.quill.setBold(vars.bold)
        pt.a.quill.setItalic(vars.italic)
        pt.a.quill.setUnderline(vars.underline)
        pt.a.quill.setColor(vars.color)


class CmdEditOrigin(CmdSceneItem):
    _item   : ItemOriginMixin
    _before : str
    _after  : str

    def __init__(
        self    : Self,
        scene   : "DrawingScene",
        item    : ItemOriginMixin,
        ap_name : str
    ):
        super().__init__(scene, item)
        self._before = item.getOrigin()
        self._after = ap_name

    def redo(self : Self) -> None:
        self._item.setOrigin(self._after)

    def undo(self : Self) -> None:
        self._item.setOrigin(self._before)
