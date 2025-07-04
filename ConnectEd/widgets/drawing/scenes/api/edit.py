__all__ = [
    "cmdEditPaste",
    "cmdEditDelete",
    "cmdEditDuplicate",
    "cmdEditMove",
    "cmdEditAppearance",
    "cmdEditProperties",
    "DrawingSceneApiEditMixin"
]

from typing import Self, Optional

from PyQt6.QtCore import QPointF
from PyQt6.QtGui  import QUndoCommand

from .....core import logger,copy, paste

from ....dialogs.properties import PropertiesType

from ...items import ElementMixin, cmdElement, cmdElements, clone, \
                     AppearancePref, AppearancePrefChange

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
            element.setKPVisible(False)  # Explicitly hide keypoints
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
                if len(self._selection) == 1:
                    element.setKPVisible(True)
                element.update()  # Force repaint
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
                # Show key points if only one element was selected
                if len(self._selection) == 1:
                    element.setKPVisible(True)
                else:
                    element.setKPVisible(False)
                element.update()
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
            element.setKPVisible(False)  # Explicitly hide keypoints
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
                if len(self._selection) == 1:
                    element.setKPVisible(True)
                element.update()  # Force repaint
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
            a = e.appearance
            p = AppearancePref()
            p.line = a.line.getPref() if a.line is not None else None
            p.fill = a.fill.getPref() if a.fill is not None else None
            p.text = a.text.getPref() if a.text is not None else None
            self._before[e] = p

    def redo(self) -> None:
        c = self._after
        for e in self._elements:
            a = e.appearance
            if a.line is not None: a.line.setPref(c.line)
            if a.fill is not None: a.fill.setPref(c.fill)
            if a.text is not None: a.text.setPref(c.text)
            e.update()

    def undo(self) -> None:
        for e in self._elements:
            a = e.appearance
            c = self._before[e]
            if a.line is not None: a.line.setPref(c.line)
            if a.fill is not None: a.fill.setPref(c.fill)
            if a.text is not None: a.text.setPref(c.text)
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
    def editCut(
        self : "DrawingScene",
        pos  : QPointF = QPointF(0, 0)
    ) -> None:
        elements = \
            [item for item in self.selectedItems() if isinstance(item, ElementMixin)]
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
            [item for item in self.selectedItems() if isinstance(item, ElementMixin)]
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
            elements = [item for item in items if isinstance(item, ElementMixin)]
        else:
            items, pos0, selection = ips
            if not isinstance(items, list):
                items = [items]
            elements = [item for item in items if isinstance(item, ElementMixin)]
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

    def editAppearance(
        self     : "DrawingScene",
        elements : list[ElementMixin],
        changes  : AppearancePrefChange
    ) -> None:
        self.undo_stack.push(cmdEditAppearance(self, elements, changes))

    def editProperties(
        self    : "DrawingScene",
        element : ElementMixin,
        changes : dict[PropertyText, tuple[str, PropertiesType, PropertiesType]]
    ) -> None:
        self.undo_stack.push(cmdEditProperties(self, element, changes))
