__all__ = ["DrawingSceneApiEditMixin"]

from typing import Self

from ...items import Element, cmdElements, AppearancePref, AppearancePrefChange

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
            a.line = None if e.line is None else e.line.get()
            a.fill = None if e.fill is None else e.fill.get()
            a.text = None if e.text is None else e.text.get()
            self._initial[e] = a

    def redo(self) -> None:
        c = self._changes
        for e in self.elements:
            if e.line is not None: e.line.set(c.line)
            if e.fill is not None: e.fill.set(c.fill)
            if e.text is not None: e.text.set(c.text)
            e.update()

    def undo(self) -> None:
        for e in self.elements:
            c = self._initial[e]
            if c.line is not None: e.line.set(c.line)
            if c.fill is not None: e.fill.set(c.fill)
            if c.text is not None: e.text.set(c.text)
            e.update()

class DrawingSceneApiEditMixin:
    def editAppearance(
        self     : "DrawingScene",
        elements : list[Element],
        changes  : AppearancePrefChange
    ) -> None:
        self.undo_stack.push(cmdEditAppearance(self, elements, changes))
