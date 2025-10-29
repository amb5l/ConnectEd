from typing import Self
from dataclasses import dataclass

from .....dialogs.properties import PropertyChange

from ....properties import PropertiesMixin

from ....items import SignalDirection, VectorRange, \
                      QuillPref, QuillPrefChange, \
                      AppearancePref, AppearancePrefChange

from ....items.mixin        import ItemMixin
from ....items.mixin.origin import ItemOriginMixin

from ....items.base_text     import BaseText
from ....items.property_text import PropertyText, PropertyDisplay
from ....items.anchor_point  import AnchorPoint

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
            item.name, item.direction, item.range
        )
        self._after  = self.PortPinState(name, direction, range)

    def redo(self : Self) -> None:
        self._item.name = self._after.name
        self._item.direction = self._after.direction
        self._item.range = self._after.range
        self._item.update()

    def undo(self : Self) -> None:
        self._item.name = self._before.name
        self._item.direction = self._before.direction
        self._item.range = self._before.range
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
        name       : str
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
        name       : str,
        value      : str,
        display    : PropertyDisplay,
        appearance : QuillPrefChange
    ):
        super().__init__(scene, item)
        self._item           = item
        self._before = self.PropertyTextState(
            item.name(), item.value(), item.display(), \
            item.a.quill.getPref()
        )
        self._after  = self.PropertyTextState(name, value, display, appearance)

    def redo(self : Self) -> None:
        self._item.setName(self._after.name)
        self._item.setValue(self._after.value)
        self._item.setDisplay(self._after.display)
        self._item.a.quill.setPref(self._after.appearance)
        self._item.update()

    def undo(self : Self) -> None:
        self._item.setName(self._before.name)
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
    _item    : PropertiesMixin
    _changes : list[PropertyChange]

    def __init__(
        self    : Self,
        scene   : "DrawingScene",
        item    : PropertiesMixin,
        changes : list[PropertyChange]
    ):
        super().__init__(scene, item)
        self._changes = changes

    def redo(self : Self) -> None:
        """
        """
        for change in self._changes:
            if change.before is None:  # new property
                self._item.addProperty(change.after.name)
                self._item.setPropertyValue(
                    change.after.name, change.after.value
                )
                self._item.setPropertyDescription(
                    change.after.name, change.after.description
                )
            else:  # existing property
                if change.after is None:  # deleted property
                    self._item.deleteProperty(change.before.name)
                else:
                    self._item.renameProperty(
                        change.before.name, change.after.name
                    )
                    self._item.setPropertyValue(
                        change.after.name, change.after.value
                    )

    def undo(self : Self) -> None:
        for change in self._changes:
            if change.before is None:  # new property
                self._item.deleteProperty(change.after.name)
            else:  # existing property
                if change.after is None:  # deleted property
                    self._item.addProperty(change.before.name)
                    self._item.setPropertyValue(
                        change.before.name, change.before.value
                    )
                    self._item.setPropertyDescription(
                        change.before.name, change.before.description
                    )
                else:
                    self._item.renameProperty(
                        change.after.name, change.before.name
                    )
                    self._item.setPropertyValue(
                        change.before.name, change.before.value
                    )
                    self._item.setPropertyDescription(
                        change.before.name, change.before.description
                    )


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
