from typing import Self, Any

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui     import QAction, QUndoStack, QUndoCommand

from ......core.check import checked

from ....items import ItemType

from ....items.block      import BlockItem
from ....items.block_pin  import BlockPinItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...drawing import DrawingView
    from ....scenes.drawing import DrawingScene


class DrawingInteraction:
    """Base for all interactions.

    ``commit``, ``complete`` and ``cancel`` are public entry points that
    track a ``_done`` flag. Once an interaction is done (``commit`` returned
    True, ``complete`` finished, or ``cancel`` ran), further calls to any
    of them are no-ops. This makes it safe for state-machine code (e.g.
    ``DrawingViewStateBase.go``) to cancel whatever interaction happens to
    be live without worrying about whether it was already committed.

    Subclasses implement the actual behaviour in ``_commit``, ``_complete``
    and ``_cancel``.
    """

    # instance attributes
    _view  : "DrawingView"
    _scene : "DrawingScene"
    _done  : bool

    @checked
    def __init__(self : Self, view : "DrawingView") -> None:
        self._view = view
        self._scene = view.scene()
        self._done = False

    def done(self : Self) -> bool:
        return self._done

    # Public entry points ---------------------------------------------------

    def commit(self : Self, *args : Any, **kwargs : Any) -> bool:
        if self._done:
            return False
        result = self._commit(*args, **kwargs)
        if result:
            self._done = True
        return result

    def complete(self : Self, *args : Any, **kwargs : Any) -> None:
        if self._done:
            return
        self._complete(*args, **kwargs)
        self._done = True

    def cancel(self : Self) -> None:
        if self._done:
            return
        self._cancel()
        self._done = True

    # Subclass hooks --------------------------------------------------------

    def valid(self : Self) -> bool:
        raise NotImplementedError("Subclass must implement this method")

    def update(self : Self, *args : Any, **kwargs : Any) -> None:
        raise NotImplementedError("Subclass must implement this method")

    def _commit(self : Self, *args : Any, **kwargs : Any) -> bool:
        raise NotImplementedError("Subclass must implement this method")

    def _complete(self : Self, *args : Any, **kwargs : Any) -> None:
        raise NotImplementedError("Subclass must implement this method")

    def _cancel(self : Self) -> None:
        raise NotImplementedError("Subclass must implement this method")

    def ctxMenuItems(self : Self, pos : QPointF) -> list[QAction | QMenu]:
        return [
            self._view.action("Cancel", self.cancel)
        ]


class DrawingItemInteraction(DrawingInteraction):
    """Base for all interactions that operate on a single scene item."""
    # instance attributes
    _item : ItemType

    @checked
    def __init__(
        self : Self,
        view : "DrawingView",
        item : ItemType
    ) -> None:
        super().__init__(view)
        self._item = item

    def valid(self : Self) -> bool:
        return self._item is not None


class DrawingItemsInteraction(DrawingInteraction):
    """Base for all interactions that operate on one or more scene items."""

    # instance attributes
    _items : list[ItemType] | None

    @checked
    def __init__(
        self  : Self,
        view  : "DrawingView",
        items : list[ItemType]
    ) -> None:
        super().__init__(view)
        self._items = items

    def valid(self : Self) -> bool:
        return self._items is not None


class RotateItemMixin:
    """Mixin for interactions that rotate items."""

    # instance attributes
    _item : ItemType

    def rotateCW(self : Self) -> None:
        self._item.setRotation((self._item.rotation() + 90) % 360)

    def rotateCCW(self : Self) -> None:
        self._item.setRotation((self._item.rotation() - 90) % 360)

    def ctxMenuItems(self : Self | DrawingInteraction, pos : QPointF) -> list[QAction | QMenu]:
        return [
            self._view.action("Rotate CW",  self.rotateCW,  "]"),
            self._view.action("Rotate CCW", self.rotateCCW, "["),
            self._view.separator(),
        ] + super().ctxMenuItems(pos)


class PreviewStateMixin:
    """Mixin for interactions that need to save/restore pre-preview state."""

    # instance attributes
    _preview_state : dict[Any, Any]

    def _previewTargets(self : Self) -> list[Any]:
        raise NotImplementedError("Subclass must define preview targets")

    def _previewSaveTarget(self : Self, target : Any) -> Any:
        raise NotImplementedError("Subclass must define target state save")

    def _previewRestoreTarget(self : Self, target : Any, state : Any) -> None:
        raise NotImplementedError("Subclass must define target state restore")

    def _previewDidRestore(self : Self) -> None:
        """Hook for interactions that need post-restore cleanup."""

    def _previewSave(self : Self) -> None:
        self._preview_state = {
            target: self._previewSaveTarget(target)
            for target in self._previewTargets()
        }

    def _previewRestore(self : Self) -> None:
        if not hasattr(self, "_preview_state"):
            return
        for target, state in self._preview_state.items():
            self._previewRestoreTarget(target, state)
        self._previewDidRestore()


class MoveItemsMixin(PreviewStateMixin):
    """Mixin for interactions that move items."""

    # instance attributes
    _items : list[ItemType]
    _ipos  : QPointF  # initial position
    _cpos  : QPointF  # current position

    def update(self : Self, pos : QPointF) -> None:
        self._moveBy(pos - self._cpos)
        self._cpos = pos

    def _moveBy(self : Self, offset : QPointF) -> None:
        for e in self._items:
            e.moveBy(offset)

    def _previewTargets(self : Self) -> list[ItemType]:
        return self._items

    def _previewSaveTarget(self : Self, target : ItemType) -> Any:
        return target.moveSave()

    def _previewRestoreTarget(self : Self, target : ItemType, state  : Any) -> None:
        target.moveRestore(state)

    def _previewDidRestore(self : Self) -> None:
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


class PreviewJournalMixin:
    """Mixin for interactions that need a preview journal (local undo stack)."""

    # instance attributes
    _preview_journal : QUndoStack

    def _previewDo(self : Self, cmd : QUndoCommand) -> None:
        self._preview_journal.push(cmd)

    def _previewUndo(self : Self) -> None:
        self._preview_journal.undo()
