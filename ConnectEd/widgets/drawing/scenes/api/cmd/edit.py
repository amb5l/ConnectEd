from typing import Self

from .....dialogs.appearance import QuillPref, QuillPrefChange, \
                                    AppearancePref, AppearancePrefChange
from .....dialogs.properties import PropertiesType

from ....items import ElementMixin, ElementOriginMixin

from ....items.base_text     import BaseText
from ....items.property_text import PropertyText

from . import cmdSceneElement, cmdSceneElements

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....scenes.drawing import DrawingScene

class cmdEditText(cmdSceneElement):
    _element           : BaseText
    _text_before       : str
    _text_after        : str
    _appearance_before : QuillPref
    _appearance_after  : QuillPrefChange

    def __init__(
        self       : Self,
        scene      : "DrawingScene",
        element    : BaseText,
        text       : str,
        appearance : QuillPrefChange
    ):
        super().__init__(scene, element)
        self._element           = element
        self._text_before       = element.text()
        self._text_after        = text
        self._appearance_before = element.quill.getPref()
        self._appearance_after  = appearance

    def redo(self : Self) -> None:
        self._element.setText(self._text_after)
        self._element.quill.setPref(self._appearance_after)
        self._element.update()

    def undo(self : Self) -> None:
        self._element.setText(self._text_before)
        self._element.quill.setPref(self._appearance_before)
        self._element.update()

class cmdEditPropertyText(cmdSceneElement):
    _element           : PropertyText
    _name_before       : str
    _name_after        : str
    _value_before      : str
    _value_after       : str
    _appearance_before : QuillPref
    _appearance_after  : QuillPrefChange

    def __init__(
        self       : Self,
        scene      : "DrawingScene",
        element    : PropertyText,
        name       : str,
        value      : str,
        appearance : QuillPrefChange
    ):
        super().__init__(scene, element)
        self._element           = element
        self._name_before       = element.name()
        self._name_after        = name
        self._value_before      = element.value()
        self._value_after       = value
        self._appearance_before = element.quill.getPref()
        self._appearance_after  = appearance

    def redo(self : Self) -> None:
        self._element.setName(self._name_after)
        self._element.setValue(self._value_after)
        self._element.quill.setPref(self._appearance_after)
        self._element.update()

    def undo(self : Self) -> None:
        self._element.setName(self._name_before)
        self._element.setValue(self._value_before)
        self._element.quill.setPref(self._appearance_before)
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
    _changes : dict[PropertyText, tuple[str, PropertiesType, PropertiesType]]

    def __init__(
        self    : Self,
        scene   : "DrawingScene",
        element : ElementMixin,
        changes : dict[PropertyText, tuple[str, PropertiesType, PropertiesType]]
    ):
        super().__init__(scene, element)
        self._changes = changes.copy()

    def redo(self: Self) -> None:
        for p in self._changes.keys():
            for label, _, after in self._changes[p]:
                setter, _ = PropertyText.TABLE_ATTRS[label]
                setter(p, after)

    def undo(self: Self) -> None:
        for p in self._changes.keys():
            for label, before, _ in self._changes[p]:
                setter, _ = PropertyText.TABLE_ATTRS[label]
                setter(p, before)

class cmdEditOrigin(cmdSceneElement):
    _element : ElementOriginMixin
    _old     : str
    _new     : str

    def __init__(
        self : Self,
        scene   : "DrawingScene",
        element : ElementOriginMixin,
        origin  : str
    ):
        super().__init__(scene, element)
        self._old = element.getOrigin()
        self._new = origin

    def redo(self : Self) -> None:
        self._element.setOrigin(self._new)

    def undo(self : Self) -> None:
        self._element.setOrigin(self._old)
