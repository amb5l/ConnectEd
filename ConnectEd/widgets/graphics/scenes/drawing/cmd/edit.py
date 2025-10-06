from typing import Self
from dataclasses import dataclass

from .....dialogs.properties import PropertyChange

from ....properties import PropertiesMixin

from ....items import SignalDirection, VectorRange, \
                      QuillPref, QuillPrefChange, \
                      AppearancePref, AppearancePrefChange

from ....items.mixin        import ElementMixin
from ....items.mixin.origin import ElementOriginMixin

from ....items.base_text     import BaseText
from ....items.property_text import PropertyText, PropertyDisplay

from . import cmdSceneElement, cmdSceneElements

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....scenes.drawing import DrawingScene
    from ....items.port_pin import PortPinMixin


class cmdEditPortPin(cmdSceneElement):
    @dataclass
    class PortPinState:
        name      : str
        direction : SignalDirection
        range     : VectorRange

    _element : "PortPinMixin"
    _before  : PortPinState
    _after   : PortPinState

    def __init__(
        self       : Self,
        scene      : "DrawingScene",
        element    : "PortPinMixin",
        name       : str,
        direction  : SignalDirection,
        range      : VectorRange
    ):
        super().__init__(scene, element)
        self._before = self.PortPinState(
            element.name, element.direction, element.range
        )
        self._after  = self.PortPinState(name, direction, range)

    def redo(self : Self) -> None:
        self._element.name = self._after.name
        self._element.direction = self._after.direction
        self._element.range = self._after.range
        self._element.update()

    def undo(self : Self) -> None:
        self._element.name = self._before.name
        self._element.direction = self._before.direction
        self._element.range = self._before.range
        self._element.update()

class cmdEditText(cmdSceneElement):
    @dataclass
    class TextState:
        text       : str
        appearance : QuillPref

    _element : BaseText
    _before  : TextState
    _after   : TextState

    def __init__(
        self       : Self,
        scene      : "DrawingScene",
        element    : BaseText,
        text       : str,
        appearance : QuillPrefChange
    ):
        super().__init__(scene, element)
        self._element           = element
        self._before = self.TextState(element.text(), element.quill.getPref())
        self._after  = self.TextState(text, appearance)

    def redo(self : Self) -> None:
        self._element.setText(self._after.text)
        self._element.quill.setPref(self._after.appearance)
        self._element.update()

    def undo(self : Self) -> None:
        self._element.setText(self._before.text)
        self._element.quill.setPref(self._before.appearance)
        self._element.update()

class cmdEditPropertyText(cmdSceneElement):
    @dataclass
    class PropertyTextState:
        name       : str
        value      : str
        display    : PropertyDisplay
        appearance : QuillPref

    _element : PropertyText
    _before  : PropertyTextState
    _after   : PropertyTextState

    def __init__(
        self       : Self,
        scene      : "DrawingScene",
        element    : PropertyText,
        name       : str,
        value      : str,
        display    : PropertyDisplay,
        appearance : QuillPrefChange
    ):
        super().__init__(scene, element)
        self._element           = element
        self._before = self.PropertyTextState(
            element.name(), element.value(), element.display(), \
            element.quill.getPref()
        )
        self._after  = self.PropertyTextState(name, value, display, appearance)

    def redo(self : Self) -> None:
        self._element.setName(self._after.name)
        self._element.setValue(self._after.value)
        self._element.setDisplay(self._after.display)
        self._element.quill.setPref(self._after.appearance)
        self._element.update()

    def undo(self : Self) -> None:
        self._element.setName(self._before.name)
        self._element.setValue(self._before.value)
        self._element.setDisplay(self._before.display)
        self._element.quill.setPref(self._before.appearance)
        self._element.update()

class cmdEditAppearance(cmdSceneElements):
    _before : dict[ElementMixin, AppearancePref]
    _after  : AppearancePrefChange

    def __init__(
        self     : Self,
        scene    : "DrawingScene",
        elements : list[ElementMixin],
        changes  : AppearancePrefChange
    ):
        super().__init__(scene, elements)
        self._after = changes
        self._before = {}
        for e in elements:
            p = AppearancePref()
            p.line  = e.line.getPref()  if hasattr(e, "line")  else None
            p.fill  = e.fill.getPref()  if hasattr(e, "fill")  else None
            p.quill = e.quill.getPref() if hasattr(e, "quill") else None
            self._before[e] = p

    def redo(self : Self) -> None:
        c = self._after
        for e in self._elements:
            if not hasattr(e, "a"):
                continue
            if e.a.line  is not None: e.a.line.setPref(c.line)
            if e.a.fill  is not None: e.a.fill.setPref(c.fill)
            if e.a.quill is not None: e.a.quill.setPref(c.quill)
            e.onGeometryChange()
            e.update()

    def undo(self : Self) -> None:
        for e in self._elements:
            c = self._before[e]
            if not hasattr(e, "a"):
                continue
            if e.a.line  is not None: e.a.line.setPref(c.line)
            if e.a.fill  is not None: e.a.fill.setPref(c.fill)
            if e.a.quill is not None: e.a.quill.setPref(c.quill)
            e.onGeometryChange()
            e.update()

class cmdEditProperties(cmdSceneElement):
    _element : PropertiesMixin
    _changes : list[PropertyChange]

    def __init__(
        self    : Self,
        scene   : "DrawingScene",
        element : PropertiesMixin,
        changes : list[PropertyChange]
    ):
        super().__init__(scene, element)
        self._changes = changes

    def redo(self : Self) -> None:
        """
        """
        for change in self._changes:
            if change.before is None:  # new property
                self._element.addProperty(change.after.name)
                self._element.setPropertyValue(
                    change.after.name, change.after.value
                )
                self._element.setPropertyDescription(
                    change.after.name, change.after.description
                )
            else:  # existing property
                if change.after is None:  # deleted property
                    self._element.deleteProperty(change.before.name)
                else:
                    self._element.renameProperty(
                        change.before.name, change.after.name
                    )
                    self._element.setPropertyValue(
                        change.after.name, change.after.value
                    )

    def undo(self : Self) -> None:
        for change in self._changes:
            if change.before is None:  # new property
                self._element.deleteProperty(change.after.name)
            else:  # existing property
                if change.after is None:  # deleted property
                    self._element.addProperty(change.before.name)
                    self._element.setPropertyValue(
                        change.before.name, change.before.value
                    )
                    self._element.setPropertyDescription(
                        change.before.name, change.before.description
                    )
                else:
                    self._element.renameProperty(
                        change.after.name, change.before.name
                    )
                    self._element.setPropertyValue(
                        change.before.name, change.before.value
                    )
                    self._element.setPropertyDescription(
                        change.before.name, change.before.description
                    )

class cmdEditOrigin(cmdSceneElement):
    _element : ElementOriginMixin
    _before  : str
    _after   : str

    def __init__(
        self : Self,
        scene   : "DrawingScene",
        element : ElementOriginMixin,
        origin  : str
    ):
        super().__init__(scene, element)
        self._before = element.getOriginAPName()
        self._after = origin

    def redo(self : Self) -> None:
        self._element.setOriginAPName(self._after)

    def undo(self : Self) -> None:
        self._element.setOriginAPName(self._before)
