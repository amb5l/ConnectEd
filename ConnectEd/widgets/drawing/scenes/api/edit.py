__all__ = ["DrawingSceneApiEditMixin"]

from typing import Self

from PyQt6.QtCore import QPointF

from .....core import logger,copy, paste

from ...items import Element, cmdElements, cmdPlaceElement, \
                     AppearancePref, AppearancePrefChange

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


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
            a.line = None if e.line is None else e.line.getPref()
            a.fill = None if e.fill is None else e.fill.getPref()
            a.text = None if e.text is None else e.text.getPref()
            self._initial[e] = a

    def redo(self) -> None:
        c = self._changes
        for e in self.elements:
            if e.line is not None: e.line.setPref(c.line)
            if e.fill is not None: e.fill.setPref(c.fill)
            if e.text is not None: e.text.setPref(c.text)
            e.update()

    def undo(self) -> None:
        for e in self.elements:
            c = self._initial[e]
            if c.line is not None: e.line.setPref(c.line)
            if c.fill is not None: e.fill.setPref(c.fill)
            if c.text is not None: e.text.setPref(c.text)
            e.update()

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
        self : "DrawingScene",
        pos  : QPointF = QPointF(0, 0)
    ) -> None:
        items, copy_pos = paste()
        if not items:
            return
        elements = [item for item in items if isinstance(item, Element)]
        if not elements:
            logger.warning("No valid elements to paste")
            return
        copy_pos = elements[0].pos() if copy_pos is None and elements else \
            copy_pos or QPointF(0, 0)
        if elements:
            self.undo_stack.beginMacro("Paste Elements")
            for item in elements:
                # Offset each item to paste relative to the provided position
                item.setPos(item.pos() + (pos - copy_pos))
                self.undo_stack.push(cmdPlaceElement(self, item))
            self.undo_stack.endMacro()

    def editAppearance(
        self     : "DrawingScene",
        elements : list[Element],
        changes  : AppearancePrefChange
    ) -> None:
        self.undo_stack.push(cmdEditAppearance(self, elements, changes))
