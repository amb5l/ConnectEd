__all__ = ["DrawingSceneApiEditMixin"]

from typing import Self, Optional

from PyQt6.QtCore import QPointF
from PyQt6.QtGui  import QUndoCommand

from .....core import logger,copy, paste

from ...items import Element, cmdElements, cmdPlaceElement, \
                     AppearancePref, AppearancePrefChange

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


class cmdEditPaste(cmdElements):
    """Command for pasting multiple elements with interactive positioning."""
    offset : QPointF

    def __init__(
        self     : Self,
        scene    : "DrawingScene",
        elements : list[Element],
        offset   : QPointF
    ):
        super().__init__(scene, elements)
        self.offset = offset

    def redo(self : Self) -> None:
        for element in self.elements:
            if element.scene() != self.scene:
                self.scene.addItem(element)
            element.setPos(element.pos() + self.offset)

    def undo(self : Self) -> None:
        for element in self.elements:
            if element.scene() == self.scene:
                self.scene.removeItem(element)

    def mergeWith(self : Self, other : QUndoCommand) -> bool:
        return super().mergeWith(other) and self.offset == other.offset

class cmdEditAppearance(cmdElements):
    _initial : dict[Element, AppearancePref]
    _changes : AppearancePrefChange

    def __init__(
        self     : Self,
        scene    : "DrawingScene",
        elements : list[Element],
        changes  : AppearancePrefChange
    ):
        super().__init__(scene, elements)
        self._changes = changes
        self._initial = {}
        for e in elements:
            a = AppearancePref()
            a.line = e.line.getPref() if hasattr(e, "line") else None
            a.fill = e.fill.getPref() if hasattr(e, "fill") else None
            a.text = e.text.getPref() if hasattr(e, "text") else None
            self._initial[e] = a

    def redo(self) -> None:
        c = self._changes
        for e in self.elements:
            if hasattr(e, "line") and e.line is not None: e.line.setPref(c.line)
            if hasattr(e, "fill") and e.fill is not None: e.fill.setPref(c.fill)
            if hasattr(e, "text") and e.text is not None: e.text.setPref(c.text)
            e.update()

    def undo(self) -> None:
        for e in self.elements:
            c = self._initial[e]
            if hasattr(e, "line") and c.line is not None: e.line.setPref(c.line)
            if hasattr(e, "fill") and c.fill is not None: e.fill.setPref(c.fill)
            if hasattr(e, "text") and c.text is not None: e.text.setPref(c.text)
            e.update()

    def mergeWith(self : Self, other : QUndoCommand) -> bool:
        return False

class DrawingSceneApiEditMixin:
    def editCopy(
        self : "DrawingScene",
        pos  : QPointF = QPointF(0, 0)
    ) -> None:
        elements = \
            [item for item in self.selectedItems() if isinstance(item, Element)]
        if elements:
            copy(elements, pos)
        else:
            logger.warning("No elements selected to copy")

    def editPaste(
        self      : "DrawingScene",
        pos       : QPointF = QPointF(0, 0),
        items_pos : Optional[tuple[Element | list[Element, QPointF]]] = None
    ) -> bool:
        if items_pos is None:
            items, pos0 = paste()
            if not items:
                logger.warning("No valid data to paste")
                return False
            elements = [item for item in items if isinstance(item, Element)]
        else:
            items, pos0 = items_pos
            if not isinstance(items, list):
                items = [items]
        elements = [item for item in items if isinstance(item, Element)]
        if not elements:
            logger.warning("No valid elements to paste")
            return False
        offset = pos - pos0
        cmd = cmdEditPaste(self, elements, offset)
        self.undo_stack.push(cmd)
        for element in elements:
            element.resetUuid() # new identity for pasted elements
            element.setSelected(True)
        return True

    def editAppearance(
        self     : "DrawingScene",
        elements : list[Element],
        changes  : AppearancePrefChange
    ) -> None:
        self.undo_stack.push(cmdEditAppearance(self, elements, changes))