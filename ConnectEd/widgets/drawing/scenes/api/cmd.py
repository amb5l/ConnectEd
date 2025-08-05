from typing import Self, Optional

from PyQt6.QtGui import QUndoCommand

from .....core import camel_to_proper

from ...items import ElementMixin


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


class cmdBase(QUndoCommand):
    """Base class for all commands."""

    _PRESERVE_SELECTION : bool = False

    _scene     : "DrawingScene"
    _selection : Optional[list[ElementMixin]]

    def __init__(self    : Self, scene   : "DrawingScene"):
        text = camel_to_proper(self.__class__.__name__.replace("cmd", ""))
        super().__init__(text)
        self._scene = scene
        if self._PRESERVE_SELECTION:
            self._selection = scene.selectedItems()

    def id(self : Self) -> int:
        """Return a unique ID for merging commands."""
        class_id = hash(self.__class__.__name__) & 0x7FFFFFFF
        return class_id

    def mergeWith(self : Self, other : QUndoCommand) -> bool:
        """Merge this command with another identical command."""
        if not isinstance(other, self.__class__) \
        or other._scene != self._scene:
            return False
        return True

    def redo(self : Self) -> None:
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement redo"
        )

    def undo(self : Self) -> None:
        if self._PRESERVE_SELECTION:
            self._scene.blockSignals(True)
            for element in self._selection:
                element.setSelected(True)
            self._scene.blockSignals(False)
            self._scene.selectionChanged.emit()

class cmdElement(cmdBase):
    """Base class for all commands that work with an element."""

    _element : ElementMixin

    def __init__(
        self    : Self,
        scene   : "DrawingScene",
        element : ElementMixin
    ):
        super().__init__(scene)
        self._element = element

    def mergeWith(self : Self, other : QUndoCommand) -> bool:
        return super().mergeWith(other) and other._element == self._element

class cmdElements(cmdBase):
    """Base class for all commands that work with multiple elements."""

    _elements  : list[ElementMixin]

    def __init__(
        self     : Self,
        scene    : "DrawingScene",
        elements : list[ElementMixin]
    ):
        super().__init__(scene)
        self._elements = elements

    def mergeWith(self : Self, other : QUndoCommand) -> bool:
        return super().mergeWith(other) and other._elements == self._elements

class cmdPlaceElement(cmdElement):
    """Base class for all commands that place an element."""

    def __init__(
        self    : Self,
        scene   : "DrawingScene",
        element : ElementMixin
    ):
        super().__init__(scene, element) # record scene and element instances

    def redo(self : Self) -> None:
        if self._element.scene() != self._scene:
            self._scene.addItem(self._element)

    def undo(self : Self) -> None:
        self._scene.removeItem(self._element)