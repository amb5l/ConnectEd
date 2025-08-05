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
            for e in self._selection:
                e.setSelected(True)
            self._scene.blockSignals(False)
            self._scene.selectionChanged.emit()

class cmdElement(cmdBase):
    """Base class for all commands that work with an element."""

    # instance attributes
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

    # instance attributes
    _elements : list[ElementMixin]

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

    def _addToScene(self : Self, select : bool = False) -> None:
        if select:
            self._scene.blockSignals(True)
            self._scene.clearSelection()
        for element in self._elements:
            if element.scene() != self._scene:
                self._scene.addItem(element)
            if select:
                element.setSelected(True)
        if select:
            self._scene.blockSignals(False)
            self._scene.selectionChanged.emit()

    def _removeFromScene(self : Self) -> None:
        for element in self._elements:
            if element.scene() == self._scene:
                self._scene.removeItem(element)

class cmdMoveMixin:
    """Mixin for commands supporting interactive movement of elements."""

    def _moveBy(self, offset: QPointF) -> None:
        for e in self._elements:
            e.moveBy(offset)

class cmdOffsetMixin:
    """Mixin for commands that move elements by an offset."""

    # instance attributes
    _spos     : dict[ElementMixin, QPointF]
    _offset   : QPointF

    @property
    def offset(self : Self) -> QPointF:
        return self._offset

    @offset.setter
    def offset(self : Self, offset: QPointF) -> None:
        self._offset = offset

    def _storePos(self) -> None:
        self._spos = {e: e.scenePos() for e in self._elements}

    def _restorePos(self) -> None:
        for e in self._elements:
            e.moveBy(self._spos[e] - e.scenePos())

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
