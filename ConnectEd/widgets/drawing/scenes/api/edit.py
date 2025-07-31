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

from ...items import ElementMixin, cmdElement, cmdElements, \
                     QuillPref, QuillPrefChange, \
                     clone

from ...items.base_text import BaseText

from ...items.property_text import PropertyText


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


class cmdEditPaste(cmdElements):
    _offset    : QPointF
    _selection : list[ElementMixin]  # selected elements before pasting

    def __init__(
        self      : Self,
        scene     : "DrawingScene",
        elements  : list[ElementMixin],
        offset    : QPointF,
        selection : list[ElementMixin] = None
    ):
        super().__init__(scene, elements)
        self._offset = offset
        self._selection = selection or []

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
        self._scene.blockSignals(True)
        for element in self._elements:
            if element.scene() == self._scene:
                self._scene.removeItem(element)
        for element in self._selection:
            if element.scene() == self._scene:
                element.setSelected(True)
        self._scene.blockSignals(False)
        self._scene.selectionChanged.emit()

    def mergeWith(self, other: QUndoCommand) -> bool:
        return super().mergeWith(other) and self._offset == other._offset

class cmdEditDelete(cmdElements):
    """Command for deleting multiple elements with selection state restoration."""
    _selection : list[ElementMixin]  # Elements that were selected before deletion

    def __init__(
        self     : Self,
        scene    : "DrawingScene",
        elements : list[ElementMixin]
    ):
        super().__init__(scene, elements)
        # Store current selection state before deletion
        self._selection = [item for item in scene.selectedItems() if isinstance(item, ElementMixin)]

    def redo(self) -> None:
        """Delete the elements from the scene."""
        self._scene.blockSignals(True)
        self._scene.clearSelection()
        for element in self._elements:
            if element.scene() == self._scene:
                self._scene.removeItem(element)
        self._scene.blockSignals(False)
        self._scene.selectionChanged.emit()

    def undo(self) -> None:
        """Restore the deleted elements and their selection state."""
        self._scene.blockSignals(True)
        for element in self._elements:
            if element.scene() != self._scene:
                self._scene.addItem(element)
        # Restore original selection state
        self._scene.clearSelection()
        for element in self._selection:
            if element.scene() == self._scene:
                element.setSelected(True)
        self._scene.blockSignals(False)
        self._scene.selectionChanged.emit()

    def mergeWith(self, other: QUndoCommand) -> bool:
        """Delete commands cannot be merged."""
        return False

class cmdEditDuplicate(cmdElements):
    _offset    : QPointF
    _selection : list[ElementMixin]  # selected elements before duplication
    _originals : list[ElementMixin]  # original elements that were duplicated

    def __init__(
        self      : Self,
        scene     : "DrawingScene",
        elements  : list[ElementMixin],
        offset    : QPointF,
        selection : list[ElementMixin] = None
    ):
        super().__init__(scene, elements)
        self._offset = offset
        self._selection = selection or []
        self._originals = []

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
        self._scene.blockSignals(True)
        for element in self._elements:
            if element.scene() == self._scene:
                self._scene.removeItem(element)
        for element in self._selection:
            if element.scene() == self._scene:
                element.setSelected(True)
        self._scene.blockSignals(False)
        self._scene.selectionChanged.emit()

    def mergeWith(self, other: QUndoCommand) -> bool:
        return super().mergeWith(other) and self._offset == other._offset

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

    def mergeWith(self : Self, other : QUndoCommand) -> bool:
        if not super().mergeWith(other):
            return False
        self._offset += other._offset
        return True

    def redo(self : Self) -> None:
        for element in self._elements:
            element.moveBy(self._offset.x(), self._offset.y())
            # TODO: add slide logic

    def undo(self : Self) -> None:
        for element in self._elements:
            element.moveBy(-self._offset.x(), -self._offset.y())
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

    def mergeWith(self : Self, other : QUndoCommand) -> bool:
        return False

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

    def mergeWith(self : Self, other : QUndoCommand) -> bool:
        return False

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

    def mergeWith(self : Self, other : QUndoCommand) -> bool:
        return False

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

    def mergeWith(self: Self, other: QUndoCommand) -> bool:
        return False

class DrawingSceneApiEditMixin:
    def editSelectAll(self : "DrawingScene") -> None:
        raise NotImplementedError("Not implemented yet")

    def editSelectArea(self : "DrawingScene") -> None:
        raise NotImplementedError("Not implemented yet")

    def editDeselectAll(self : "DrawingScene") -> None:
        raise NotImplementedError("Not implemented yet")

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

    def editPaste(
        self : "DrawingScene",
        pos  : QPointF = QPointF(0, 0),
        ips  : Optional[tuple[ElementMixin | list[ElementMixin], QPointF, list[ElementMixin]]] = None
    ) -> bool:
        if ips is None:
            items, pos0 = paste()
            selection = []
            if not items:
                logger.warning("No valid data to paste")
                return False
            elements = items # no filtering at the moment
        else:
            items, pos0, selection = ips
            if not isinstance(items, list):
                items = [items]
            elements = items # no filtering at the moment
        if not elements:
            logger.warning("No valid elements to paste")
            return False
        self.clearSelection()
        offset = pos - pos0
        self.undo_stack.push(cmdEditPaste(self, elements, offset, selection))
        for element in elements:
            element.resetUuid()  # new identity for pasted elements
        return True

    def editDelete(
        self : "DrawingScene"
    ) -> None:
        """Delete selected elements from the scene."""
        elements = \
            [item for item in self.selectedItems() if isinstance(item, ElementMixin)]
        if elements:
            self.undo_stack.push(cmdEditDelete(self, elements))
        else:
            logger.warning("No elements selected to delete")

    def editDuplicate(
        self : "DrawingScene",
        pos  : QPointF = QPointF(0, 0),
        ips  : Optional[tuple[ElementMixin | list[ElementMixin], QPointF, list[ElementMixin]]] = None
    ) -> bool:
        """Duplicate selected elements."""
        if ips is None:
            elements = [item for item in self.selectedItems() if isinstance(item, ElementMixin)]
            if not elements:
                logger.warning("No elements selected to duplicate")
                return False
            clones = clone(elements)
            pos0 = elements[0].pos() if elements else QPointF(0, 0)
            selection = []
        else:
            originals, pos0, selection = ips
            if not isinstance(originals, list):
                originals = [originals]
            elements = [item for item in originals if isinstance(item, ElementMixin)]
            if not elements:
                logger.warning("No valid elements to duplicate")
                return False
            clones = clone(elements)
        if not clones:
            logger.warning("No valid elements to duplicate")
            return False
        self.clearSelection()
        offset = pos - pos0
        self.undo_stack.push(cmdEditDuplicate(self, clones, offset, selection))
        return True

    def editMove(
        self     : "DrawingScene",
        elements : list[ElementMixin],
        offset   : QPointF,
        slide    : bool = False
    ) -> None:
        self.undo_stack.push(cmdEditMove(self, elements, offset, slide))

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
