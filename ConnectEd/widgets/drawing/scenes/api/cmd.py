from typing import Self, Optional

from PyQt6.QtCore import QPointF
from PyQt6.QtGui  import QUndoCommand

from .....core import camel_to_proper

from ...items import ElementMixin


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


class cmdBase(QUndoCommand):
    """Base class for all commands."""

    # class attributes
    _PREVIEW   : bool = False  # supports preview phase
    _SELECTION : bool = False  # preserves selection set

    # instance attributes
    _scene     : "DrawingScene"
    _selection : Optional[list[ElementMixin]]

    def __init__(self    : Self, scene   : "DrawingScene"):
        text = camel_to_proper(self.__class__.__name__.replace("cmd", ""))
        super().__init__(text)
        self._scene = scene
        if self._SELECTION and not self._PREVIEW:
            self._selection = self._scene.selectedItems()

    def id(self : Self) -> int:
        """Return a unique ID for merging commands."""
        class_id = hash(self.__class__.__name__) & 0x7FFFFFFF
        return class_id

    def mergeWith(self : Self, other : QUndoCommand) -> bool:
        """Merge this command with another identical command."""
        # return isinstance(other, self.__class__) and other._scene == self._scene
        return False

    def begin(self : Self) -> None:
        if self._PREVIEW:
            if self._SELECTION:
                self._selection = self._scene.selectedItems()
        else:
            raise NotImplementedError(
                f"{self.__class__.__name__} does not support preview"
            )

    def cancel(self : Self) -> None:
        if self._PREVIEW:
            self.undo()
        else:
            raise NotImplementedError(
                f"{self.__class__.__name__} does not support preview"
            )

    def redo(self : Self) -> None:
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement redo"
        )

    def undo(self : Self) -> None:
        if self._SELECTION:
            self._scene.blockSignals(True)
            self._scene.clearSelection()
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

    @property
    def element(self : Self) -> ElementMixin:
        return self._element

    def mergeWith(self : Self, other : QUndoCommand) -> bool:
        # return super().mergeWith(other) and other._element == self._element
        return False

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

    @property
    def elements(self):
        return self._clones

    def mergeWith(self : Self, other : QUndoCommand) -> bool:
        # return super().mergeWith(other) and other._elements == self._elements
        return False

class cmdPlaceElement(cmdBase):
    """Base class for all commands that place an element."""

    # class attributes
    _PREVIEW   = True
    _SELECTION = True
    _CLASS : ElementMixin

    # instance attributes
    _element : ElementMixin

    def __init__(self : Self, scene : "DrawingScene"):
        super().__init__(scene)

    def begin(self : Self, pos : QPointF) -> None:
        super().begin() # preserve selection set
        self._element = self._CLASS(pos)
        self._element.setSelected(True)
        self._scene.addItem(self._element)

    @property
    def element(self : Self) -> ElementMixin:
        return self._element

    def redo(self : Self) -> None:
        if self._element.scene() != self._scene:
            self._scene.addItem(self._element)

    def undo(self : Self) -> None:
        super().undo() # restore selection set
        self._scene.removeItem(self._element)
