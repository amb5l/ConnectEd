from typing import Self
from dataclasses import dataclass

from PyQt6.QtCore import QPointF

from .....dialogs.properties import DisplayChoice, PropertyVariables, PropertyChange

from ....properties import PropertiesMixin

from ....items import SignalDirection, VectorRange, \
                      QuillPref, QuillPrefChange, \
                      AppearancePref, AppearancePrefChange

from ....items.mixin        import ItemMixin
from ....items.mixin.origin import ItemOriginMixin
from ....items.mixin.anchor import ItemAnchorPointsMixin

from ....items.anchor_point  import AnchorPoint
from ....items.polyline      import Polyline, PolySeg
from ....items.base_text     import BaseText
from ....items.property_text import PropertyDisplay, PropertyText

from . import CmdSceneItem, CmdSceneItems

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

    _item   : BaseText
    _before : TextState
    _after  : TextState

    def __init__(
        self       : Self,
        scene      : "DrawingScene",
        item       : BaseText,
        text       : str,
        appearance : QuillPrefChange
    ):
        super().__init__(scene, item)
        self._item           = item
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
        display    : PropertyDisplay
        appearance : QuillPref

    _item   : PropertyText
    _before : PropertyTextState
    _after  : PropertyTextState

    def __init__(
        self       : Self,
        scene      : "DrawingScene",
        item       : PropertyText,
        value      : str,
        display    : PropertyDisplay,
        appearance : QuillPrefChange
    ):
        super().__init__(scene, item)
        self._item           = item
        self._before = self.PropertyTextState(
            item.value(), item.display(), item.a.quill.getPref()
        )
        self._after  = self.PropertyTextState(value, display, appearance)

    def redo(self : Self) -> None:
        self._item.setValue(self._after.value)
        self._item.setDisplay(self._after.display)
        self._item.a.quill.setPref(self._after.appearance)
        self._item.update()

    def undo(self : Self) -> None:
        self._item.setValue(self._before.value)
        self._item.setDisplay(self._before.display)
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


class CmdEditProperties(CmdSceneItem):
    _item    : PropertiesMixin | ItemAnchorPointsMixin
    _changes : dict[str, PropertyChange]

    def __init__(
        self    : Self,
        scene   : "DrawingScene",
        item    : PropertiesMixin,
        changes : dict[str, PropertyChange]
    ):
        super().__init__(scene, item)
        self._changes = changes

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
                self._item.addProperty(after.name, after.value)
                if after.display != DisplayChoice.NONE:
                    self._addPropertyText(after)
            elif after is None:
                # delete property
                pt = self._item.getPropertyText(before.name)
                if pt is not None:
                    self._item.delPropertyText(before.name)
                self._item.delProperty(before.name)
            else:
                # existing property
                self._item.renProperty(before.name, after.name)
                self._item.setPropertyValue(after.name, after.value)
                pt = self._item.getPropertyText(before.name)
                if pt is None:
                    if after.display != DisplayChoice.NONE:
                        self._addPropertyText(after)
                else:
                    if after.display == DisplayChoice.NONE:
                        self._item.delPropertyText(before.name)
                    else:
                        self._modifyPropertyText(pt, after)

    def _addPropertyText(self : Self, vars : PropertyVariables) -> None:
        pt = PropertyText()
        self._modifyPropertyText(pt, vars)
        pt.setParentItem(self._item.getAnchorPoint(vars.cleat))
        self._item.addPropertyText(vars.name, pt)
        pt.onTextChange()  # Refresh text after parenting

    def _modifyPropertyText(
        self : Self,
        pt   : PropertyText,
        vars : PropertyVariables
    ) -> None:
        pt.setName(vars.name)
        match vars.display:
            case DisplayChoice.VALUE:
                display = PropertyDisplay.VALUE
                visible = True
            case DisplayChoice.NAME_VALUE:
                display = PropertyDisplay.NAME_VALUE
                visible = True
            case DisplayChoice.HIDDEN_VALUE:
                display = PropertyDisplay.VALUE
                visible = False
            case DisplayChoice.HIDDEN_NAME_VALUE:
                display = PropertyDisplay.NAME_VALUE
                visible = False
        pt.setVisible(visible)
        pt.setDisplay(display)
        pt.setCleatAPName(vars.cleat)
        pt.setPos(QPointF(vars.offset_x, vars.offset_y))
        pt.setOriginAPName(vars.origin)
        pt.a.quill.setFamily(vars.font)
        pt.a.quill.setSize(vars.size)
        pt.a.quill.setBold(vars.bold)
        pt.a.quill.setItalic(vars.italic)
        pt.a.quill.setUnderline(vars.underline)
        pt.a.quill.setColor(vars.color)


class CmdEditOrigin(CmdSceneItem):
    _item   : ItemOriginMixin
    _before : AnchorPoint
    _after  : AnchorPoint

    def __init__(
        self : Self,
        scene   : "DrawingScene",
        origin  : AnchorPoint
    ):
        item : ItemOriginMixin = origin.parentItem()
        super().__init__(scene, origin.parentItem())
        self._before = item.getOriginAP()
        self._after = origin

    def redo(self : Self) -> None:
        self._item.setOriginAP(self._after)

    def undo(self : Self) -> None:
        self._item.setOriginAP(self._before)
