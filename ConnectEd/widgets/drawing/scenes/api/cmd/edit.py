from typing import Self, Any
from dataclasses import dataclass

from .....dialogs.appearance import QuillPref, QuillPrefChange, \
                                    AppearancePref, AppearancePrefChange
from .....dialogs.properties import PropertyState

from ....properties import PropertiesMixin

from ....items import SignalDirection, VectorRange, \
                      ElementMixin, ElementOriginMixin

from ....items.port_pin      import BasePortPin
from ....items.base_text     import BaseText
from ....items.property_text import PropertyText, PropertyDisplay

from . import cmdSceneElement, cmdSceneElements

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....scenes.drawing import DrawingScene

class cmdEditPortPin(cmdSceneElement):
    @dataclass
    class BasePortPinState:
        name      : str
        direction : SignalDirection
        range     : VectorRange

    _element : BasePortPin
    _before  : BasePortPinState
    _after   : BasePortPinState

    def __init__(
        self       : Self,
        scene      : "DrawingScene",
        element    : BasePortPin,
        name       : str,
        direction  : SignalDirection,
        range      : VectorRange
    ):
        super().__init__(scene, element)
        self._before = self.BasePortPinState(
            element.name, element.direction, element.range
        )
        self._after  = self.BasePortPinState(name, direction, range)

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

    def redo(self) -> None:
        c = self._after
        for e in self._elements:
            if hasattr(e, "line"):  e.line.setPref(c.line)
            if hasattr(e, "fill"):  e.fill.setPref(c.fill)
            if hasattr(e, "quill"): e.quill.setPref(c.quill)
            e.onGeometryChange()
            e.update()

    def undo(self) -> None:
        for e in self._elements:
            c = self._before[e]
            if hasattr(e, "line"):  e.line.setPref(c.line)
            if hasattr(e, "fill"):  e.fill.setPref(c.fill)
            if hasattr(e, "quill"): e.quill.setPref(c.quill)
            e.onGeometryChange()
            e.update()

class cmdEditProperties(cmdSceneElement):
    _element : PropertiesMixin
    _before  : dict[str, PropertyState]
    _after   : dict[str, PropertyState]

    def __init__(
        self    : Self,
        scene   : "DrawingScene",
        element : PropertiesMixin,
        changes : dict[PropertyText, tuple[str, PropertyState]]
    ):
        super().__init__(scene, element)
        self._before = {}
        self._after = {}
        for name, change in changes.items():
            self._before[name] = PropertyState(
                name,
                element.getPropertyValue(name),
                element.getPropertyDescription(name)
            )
            self._after[name] = change

    def redo(self: Self) -> None:
        for name, change in self._after.items():
            self._element.renameProperty(change.name, name)
            self._element.setPropertyValue(name, change.value)
            self._element.setPropertyDescription(name, change.description)

    def undo(self: Self) -> None:
        for name, change in self._before.items():
            self._element.renameProperty(name, change.name)
            self._element.setPropertyValue(name, change.value)
            self._element.setPropertyDescription(name, change.description)

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
        self._before = element.getOrigin()
        self._after = origin

    def redo(self : Self) -> None:
        self._element.setOrigin(self._after)

    def undo(self : Self) -> None:
        self._element.setOrigin(self._before)
