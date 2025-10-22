from typing import Self
from abc import ABC, abstractmethod

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem, QMenu
from PyQt6.QtGui     import QAction

from ....items import ElementMixin

from ....items.block      import Block
from ....items.block_pin  import BlockPin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....scenes.drawing import DrawingScene


ElementType = ElementMixin | QGraphicsItem


class RotateMixin:
    # instance attributes
    _element : ElementType

    def rotateCW(self : Self) -> None:
        self._element.setRotation((self._element.rotation() + 90) % 360)

    def rotateCCW(self : Self) -> None:
        self._element.setRotation((self._element.rotation() - 90) % 360)


class Interaction(ABC):
    """Base for all interactions."""

    # instance attributes
    _scene        : "DrawingScene"

    def __init__(self : Self, scene : "DrawingScene"):
        self._scene = scene

    @abstractmethod
    def valid(self : Self) -> bool: ...

    @abstractmethod
    def update(self : Self, pos : QPointF) -> None: ...

    @abstractmethod
    def complete(self : Self, pos : QPointF) -> bool:
        """
        Returns True if the interaction actually completed.
        For example, if wire placement ended at an entry.
        """
        ...

    @abstractmethod
    def cancel(self : Self) -> None: ...

    def ctxMenuItems(self : Self, pos : QPointF) -> list[QAction | QMenu]:
        complete_action = QAction("Complete")
        complete_action.triggered.connect(lambda: self.complete(pos))
        cancel_action = QAction("Cancel")
        cancel_action.triggered.connect(self.cancel)
        return [complete_action, cancel_action]


class SceneElementInteraction(Interaction):
    """Base for all interactions that operate on a single scene element."""
    # instance attributes
    _element : ElementType

    def __init__(
        self    : Self,
        scene   : "DrawingScene",
        element : ElementType
    ) -> None:
        Interaction.__init__(self, scene)
        self._element = element

    @property
    def valid(self : Self) -> bool:
        return self._element is not None


class SceneElementsInteraction(Interaction):
    """Base for all interactions that operate on one or more scene elements."""

    # instance attributes
    _elements : list[ElementType]

    def __init__(
        self     : Self,
        scene    : "DrawingScene",
        elements : list[ElementType]
    ) -> None:
        Interaction.__init__(self, scene)
        self._elements = elements

    @property
    def valid(self : Self) -> bool:
        return self._elements is not None


class BlockPinInteraction(Interaction):
    """Base for all interactions that operate on a block pin."""

    # instance attributes
    _parent : Block
    _pin    : BlockPin

    def __init__(
        self   : Self,
        scene  : "DrawingScene",
        parent : Block,
        pin    : BlockPin | None,
        pos    : QPointF,
        snap   : QPointF | None = None
    ) -> None:
        Interaction.__init__(self, scene)
        if isinstance(parent, Block):
            self._parent = parent
            self._pin = pin or BlockPin(parent)
            self._pin.setParentItem(parent)
            self.update(pos, snap)
        else:
            self._parent = None
            self._pin = None

    @property
    def valid(self : Self) -> bool:
        return \
            self._parent is not None and \
            hasattr(self, "_pin") and \
            self._pin is not None


class MoveMixin:
    """Mixin for interactions that move elements."""
    # instance attributes
    _ipos : QPointF                     # initial position
    _cpos : QPointF                     # current position
    _spos : dict[ElementType, QPointF]  # stored positions

    def update(self : Self, pos : QPointF):
        self._moveBy(pos - self._cpos)
        self._cpos = pos

    def _moveBy(self : Self, offset : QPointF) -> None:
        for e in self._elements:
            e.moveBy(offset)

    def _storePos(self : Self) -> None:
        self._spos = {e: e.scenePos() for e in self._elements}

    def _restorePos(self : Self) -> None:
        for e in self._elements:
            e.moveBy(self._spos[e] - e.scenePos())
        self._cpos = self._ipos


class AddRemoveMixin:
    """Mixin for interactions that add or remove elements from the scene."""

    # instance attributes
    _scene : "DrawingScene"

    def _addToScene(self : Self, select : bool = True) -> None:
            self._scene.blockSignals(True)
            self._scene.clearSelection()
            for element in self._elements:
                if element.scene() != self._scene:
                    self._scene.addItem(element)
                if select:
                    element.setSelected(True)
            self._scene.blockSignals(False)
            self._scene.selectionChanged.emit()

    def _removeFromScene(self : Self) -> None:
        for element in self._elements:
            if element.scene() == self._scene:
                self._scene.removeItem(element)


class SelectionMixin:
    """Mixin for interactions that preserve/restore the selection."""

    # instance attributes
    _selection : list[ElementType] | None
    _scene     : "DrawingScene"

    def _preserveSelection(self : Self) -> None:
        self._selection = self._scene.selectedItems().copy() # TODO: is copy needed?

    def _restoreSelection(self : Self) -> None:
        self._scene.blockSignals(True)
        self._scene.clearSelection()
        for element in self._selection:
            element.setSelected(True)
        self._scene.blockSignals(False)
        self._scene.selectionChanged.emit()


