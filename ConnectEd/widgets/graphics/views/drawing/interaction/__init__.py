from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui     import QAction

from ....items import ItemType

from ....items.block      import Block
from ....items.block_pin  import BlockPin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...drawing import DrawingView
    from ....scenes.drawing import DrawingScene


class Interaction:
    """Base for all interactions."""

    # instance attributes
    _view  : "DrawingView"
    _scene : "DrawingScene"

    def __init__(self : Self, view : "DrawingView"):
        self._view = view
        self._scene = view.scene()

    @property
    def valid(self : Self) -> bool:
        raise NotImplementedError("Subclass must implement this method")

    def update(self : Self, pos : QPointF) -> None:
        raise NotImplementedError("Subclass must implement this method")

    def commit(self : Self, pos : QPointF) -> bool:
        raise NotImplementedError("Subclass must implement this method")

    def revert(self : Self) -> None:
        raise NotImplementedError("Subclass must implement this method")

    def complete(self : Self, pos : QPointF) -> None:
        raise NotImplementedError("Subclass must implement this method")

    def cancel(self : Self) -> None:
        raise NotImplementedError("Subclass must implement this method")

    def ctxMenuItems(self : Self, pos : QPointF) -> list[QAction | QMenu]:
        raise NotImplementedError("Subclass must implement this method")


class ItemInteraction(Interaction):
    """Base for all interactions that operate on a single scene item."""
    # instance attributes
    _item : ItemType

    def __init__(
        self : Self,
        view : "DrawingView",
        item : ItemType
    ) -> None:
        super().__init__(view)
        self._item = item

    @property
    def valid(self : Self) -> bool:
        return self._item is not None


class ItemsInteraction(Interaction):
    """Base for all interactions that operate on one or more scene items."""

    # instance attributes
    _items : list[ItemType]

    def __init__(
        self  : Self,
        view  : "DrawingView",
        items : list[ItemType]
    ) -> None:
        super().__init__(view)
        self._items = items

    @property
    def valid(self : Self) -> bool:
        return self._items is not None


class BlockPinInteraction(Interaction):
    """Base for all interactions that operate on a block pin."""

    # instance attributes
    _parent : Block
    _pin    : BlockPin

    def __init__(
        self   : Self,
        view   : "DrawingView",
        parent : Block,
        pin    : BlockPin | None,
        pos    : QPointF,
        snap   : QPointF | None = None
    ) -> None:
        super().__init__(view)
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


class RotateItemMixin:
    """Mixin for interactions that rotate items."""

    # instance attributes
    _item : ItemType

    def rotateCW(self : Self) -> None:
        self._item.setRotation((self._item.rotation() + 90) % 360)

    def rotateCCW(self : Self) -> None:
        self._item.setRotation((self._item.rotation() - 90) % 360)


class MoveItemsMixin:
    """Mixin for interactions that move items."""

    # instance attributes
    _items : list[ItemType]
    _ipos  : QPointF                     # initial position
    _cpos  : QPointF                     # current position
    _spos  : dict[ItemType, QPointF]  # stored positions

    def update(self : Self, pos : QPointF):
        self._moveBy(pos - self._cpos)
        self._cpos = pos

    def _moveBy(self : Self, offset : QPointF) -> None:
        for e in self._items:
            e.moveBy(offset)

    def _storePos(self : Self) -> None:
        self._spos = {e: e.scenePos() for e in self._items}

    def _restorePos(self : Self) -> None:
        for e in self._items:
            e.moveBy(self._spos[e] - e.scenePos())
        self._cpos = self._ipos


class AddRemoveItemsMixin:
    """Mixin for interactions that add or remove items from the scene."""

    # instance attributes
    _scene : "DrawingScene"
    _items : list[ItemType]

    def _addToScene(self : Self, select : bool = True) -> None:
            self._scene.blockSignals(True)
            self._scene.clearSelection()
            for item in self._items:
                if item.scene() != self._scene:
                    self._scene.addItem(item)
                if select:
                    item.setSelected(True)
            self._scene.blockSignals(False)
            self._scene.selectionChanged.emit()

    def _removeFromScene(self : Self) -> None:
        for item in self._items:
            if item.scene() == self._scene:
                self._scene.removeItem(item)


class SelectionMixin:
    """Mixin for interactions that preserve/restore the selection."""

    # instance attributes
    _selection : list[ItemType] | None
    _scene     : "DrawingScene"

    def _preserveSelection(self : Self) -> None:
        self._selection = self._scene.selectedItems().copy() # TODO: is copy needed?

    def _restoreSelection(self : Self) -> None:
        self._scene.blockSignals(True)
        self._scene.clearSelection()
        for item in self._selection:
            item.setSelected(True)
        self._scene.blockSignals(False)
        self._scene.selectionChanged.emit()
