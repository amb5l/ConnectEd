__all__ = [
    "cmdEditPaste",
    "cmdEditDelete",
    "cmdEditDuplicate",
    "cmdEditMove",
    "cmdEditText",
    "cmdEditPropertyText",
    "cmdEditAppearance",
    "cmdEditProperties",
    "DrawingSceneApiEditMixin"
]

from typing import Self, Optional

from PyQt6.QtCore import QPointF
from PyQt6.QtGui  import QUndoCommand

from .....core import logger,copy, paste

from ....dialogs.appearance import AppearancePref, AppearancePrefChange
from ....dialogs.properties import PropertiesType

from ...items import ElementMixin, QuillPref, QuillPrefChange, clone

from ...items.base_text import BaseText

from ...items.property_text import PropertyText

from .cmd import cmdBase, cmdElement, cmdElements


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


class cmdEditPaste(cmdElements):
    _PREVIEW   = True
    _SELECTION = True

    _offset    : QPointF

    def __init__(
        self      : Self,
        scene     : "DrawingScene",
        elements  : list[ElementMixin],
        offset    : QPointF
    ):
        super().__init__(scene, elements)
        self._offset = offset

    def redo(self) -> None:
        self._scene.blockSignals(True)
        self._scene.clearSelection()
        for element in self._elements:
            if element.scene() != self._scene:
                self._scene.addItem(element)
            element.setPos(element.pos() + self._offset)
            element.setSelected(True)
        self._scene.blockSignals(False)
        self._scene.selectionChanged.emit()

    def undo(self) -> None:
        super().undo() # restore selection set
        for element in self._elements:
            if element.scene() == self._scene:
                self._scene.removeItem(element)

class cmdEditDelete(cmdElements):
    _SELECTION = True

    def __init__(
        self     : Self,
        scene    : "DrawingScene",
        elements : list[ElementMixin]
    ):
        super().__init__(scene, elements)

    def redo(self) -> None:
        """Delete the elements from the scene."""
        self._scene.blockSignals(True)
        self._scene.clearSelection()
        for element in self._elements:
            self._scene.removeItem(element) # TODO is element in scene?
        self._scene.blockSignals(False)
        self._scene.selectionChanged.emit()

    def undo(self) -> None:
        self._scene.blockSignals(True)
        for element in self._elements:
            self._scene.addItem(element)
        super().undo() # restore selection set, should include restored elements

class cmdEditDuplicate(cmdElements):
    _PREVIEW   = True
    _SELECTION = True

    _clones : list[ElementMixin]

    def __init__(
        self     : Self,
        scene    : "DrawingScene",
        elements : list[ElementMixin]
    ):
        super().__init__(scene, elements)

    def begin(self) -> None:
        super().begin() # preserve selection set
        self._clones = clone(self._elements)
        self._addToScene()

    @property
    def elements(self):
        return self._clones

    def redo(self) -> None:
        self._addToScene()

    def undo(self) -> None:
        super().undo() # restore selection set
        for element in self._clones:
            self._scene.removeItem(element)

    def _addToScene(self) -> None:
        self._scene.blockSignals(True)
        self._scene.clearSelection()
        for element in self._clones:
            if element.scene() != self._scene:
                self._scene.addItem(element)
            element.setSelected(True)
        self._scene.blockSignals(False)
        self._scene.selectionChanged.emit()

class cmdEditMove(cmdElements):
    _offset : QPointF
    _slide  : bool

    def __init__(
        self     : Self,
        scene    : "DrawingScene",
        elements : list[ElementMixin],
        offset   : QPointF,
        slide    : bool = False
    ):
        super().__init__(scene, elements)
        self._offset = offset
        self._slide = slide

    def redo(self : Self) -> None:
        for element in self._elements:
            element.moveBy(self._offset)
            # TODO: add slide logic

    def undo(self : Self) -> None:
        for element in self._elements:
            element.moveBy(-self._offset)
            # TODO: add slide logic

class cmdEditText(cmdElement):
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

class cmdEditPropertyText(cmdElement):
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

class cmdEditAppearance(cmdElements):
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

class cmdEditProperties(cmdElement):
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

class DrawingSceneApiEditMixin:
    def editCut(
        self : "DrawingScene",
        pos  : QPointF = QPointF(0, 0)
    ) -> None:
        elements = \
            [item for item in self.selectedItems() \
                if isinstance(item, ElementMixin) \
                and item.parentItem() is None]
        if elements:
            copy(elements, pos)
            self.undo_stack.push(cmdEditDelete(self, elements))
        else:
            logger.warning("No elements selected to cut")

    def editCopy(
        self : "DrawingScene",
        pos  : QPointF = QPointF(0, 0)
    ) -> None:
        elements = \
            [item for item in self.selectedItems() \
                if hasattr(item, "toXml") \
                and item.parentItem() is None]
        if elements:
            copy(elements, pos)
        else:
            logger.warning("No elements selected to copy")

    def editDelete(
        self : "DrawingScene"
    ) -> None:
        """Delete selected elements from the scene."""
        elements = self._selectedTopElements()
        if elements:
            self.undo_stack.push(cmdEditDelete(self, elements))
        else:
            logger.warning("No elements selected to delete")

    def editSelectArea(self : "DrawingScene") -> None:
        raise NotImplementedError("Not implemented yet")

    def editSelectAll(self : "DrawingScene") -> None:
        raise NotImplementedError("Not implemented yet")

    def editText(
        self       : "DrawingScene",
        element    : BaseText,
        text       : str,
        appearance : QuillPrefChange
    ) -> None:
        self.undo_stack.push(cmdEditText(self, element, text, appearance))

    def editPropertyText(
        self       : "DrawingScene",
        element    : PropertyText,
        name       : str,
        value      : str,
        appearance : QuillPrefChange
    ) -> None:
        self.undo_stack.push(cmdEditPropertyText(
            self, element, name, value, appearance
        ))

    def editProperties(
        self    : "DrawingScene",
        element : ElementMixin,
        changes : dict[PropertyText, tuple[str, PropertiesType, PropertiesType]]
    ) -> None:
        self.undo_stack.push(cmdEditProperties(self, element, changes))

    def editAppearance(
        self     : "DrawingScene",
        elements : list[ElementMixin],
        changes  : AppearancePrefChange
    ) -> None:
        self.undo_stack.push(cmdEditAppearance(self, elements, changes))
