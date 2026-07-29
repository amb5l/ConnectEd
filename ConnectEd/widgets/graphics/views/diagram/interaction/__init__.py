from __future__ import annotations

from typing import Self, Any, Protocol, cast, Generic, TypeVar

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem, QMenu
from PyQt6.QtGui     import QAction, QUndoStack, QUndoCommand

from ......core.check import checked

from ....items.block     import BlockItem
from ....items.block_pin import BlockPinItem

from ....items.mixin import ItemMoveMixin

from .host import asDiagramInteraction, asDiagramItemInteraction

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....scenes.diagram import DiagramScene
    from .. import DiagramView
    from . import DiagramInteraction


class DiagramInteraction:
    """Base for all interactions.

    ``commit``, ``complete`` and ``cancel`` are public entry points that
    track a ``_done`` flag. Once an interaction is done (``commit`` returned
    True, ``complete`` finished, or ``cancel`` ran), further calls to any
    of them are no-ops. This makes it safe for state-machine code (e.g.
    ``DiagramViewStateBase.go``) to cancel whatever interaction happens to
    be live without worrying about whether it was already committed.

    Subclasses implement the actual behaviour in ``_commit``, ``_complete``
    and ``_cancel``.
    """

    # instance attributes
    _view  : DiagramView
    _scene : DiagramScene
    _done  : bool

    @checked
    def __init__(self : Self, view : DiagramView) -> None:
        self._view = view
        if (scene := view.scene()) is None:
            raise TypeError("Bad scene")
        self._scene = scene
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

    @checked
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


TItem = TypeVar("TItem", bound=QGraphicsItem)


class DiagramItemInteraction(DiagramInteraction, Generic[TItem]):
    """Base for all interactions that operate on a single scene item."""
    # instance attributes
    _item : TItem

    @checked
    def __init__(
        self : Self,
        view : DiagramView,
        item : TItem
    ) -> None:
        super().__init__(view)
        self._item = item

    def valid(self : Self) -> bool:
        return self._item is not None


class DiagramItemsInteraction(DiagramInteraction):
    """Base for all interactions that operate on one or more scene items."""

    # instance attributes
    _items : list[QGraphicsItem]

    @checked
    def __init__(
        self  : Self,
        view  : DiagramView,
        items : QGraphicsItem | list[QGraphicsItem]
    ) -> None:
        super().__init__(view)
        if not isinstance(items, list):
            items = [items]
        self._items = items

    def valid(self : Self) -> bool:
        return self._items is not None


class CtxMenuHost(Protocol):
    def ctxMenuItems(self, pos : QPointF) -> list[QAction | QMenu]: ...


class RotateItemMixin:
    """Mixin for interactions that rotate items."""

    def rotateCW(self : Self) -> None:
        host = asDiagramItemInteraction(self)
        host._item.setRotation((host._item.rotation() + 90) % 360)

    def rotateCCW(self : Self) -> None:
        host = asDiagramItemInteraction(self)
        host._item.setRotation((host._item.rotation() - 90) % 360)

    def ctxMenuItems(self : Self, pos : QPointF) -> list[QAction | QMenu]:
        host = asDiagramInteraction(self)
        mro_next = cast(CtxMenuHost, super())
        return [
            host._view.action("Rotate CW",  self.rotateCW,  shortcut="]"),
            host._view.action("Rotate CCW", self.rotateCCW, shortcut="["),
            host._view.separator(),
        ] + mro_next.ctxMenuItems(pos)


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
        pass

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


class MoveBaseMixin(PreviewStateMixin):
    """Mixin for interactions that move items."""

    # instance attributes
    _ipos  : QPointF                # initial position
    _cpos  : QPointF | None = None  # current position

    def update(self : Self, pos : QPointF) -> None:
        if pos == self._cpos:
            return  # filter redundant updates
        if isinstance(self._cpos, QPointF):
            self._moveBy(pos - self._cpos)
        self._cpos = pos

    def _moveBy(self : Self, offset : QPointF) -> None:
        raise NotImplementedError("Subclass must implement this method")

    def _previewSaveTarget(
        self   : Self,
        target : QGraphicsItem
    ) -> Any:
        if not isinstance(target, ItemMoveMixin):
            raise TypeError("Bad target")
        return target.moveSave()

    def _previewRestoreTarget(
        self   : Self,
        target : QGraphicsItem,
        state  : QPointF
    ) -> None:
        if not isinstance(target, ItemMoveMixin):
            raise TypeError("Bad target")
        target.moveRestore(state)

    def _previewDidRestore(self : Self) -> None:
        self._cpos = self._ipos


class MoveItemMixin(MoveBaseMixin, Generic[TItem]):
    """Mixin for interactions that move an item."""

    # instance attributes
    _item : TItem

    def _moveBy(self : Self, offset : QPointF) -> None:
        self._item.moveBy(offset.x(), offset.y())

    def _previewTargets(self : Self) -> list[QGraphicsItem]:
        return [self._item]


class MoveItemsMixin(MoveBaseMixin):
    """Mixin for interactions that move items."""

    # instance attributes
    _items : list[QGraphicsItem]

    def _moveBy(self : Self, offset : QPointF) -> None:
        for e in self._items:
            e.moveBy(offset.x(), offset.y())

    def _previewTargets(self : Self) -> list[QGraphicsItem]:
        return self._items


class AddRemoveItemsMixin:
    """Mixin for interactions that add or remove items from the scene."""

    # instance attributes
    _scene : DiagramScene
    _items : list[QGraphicsItem]

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


class DiagramBlockPinInteraction(DiagramInteraction):
    """Base for all interactions that operate on a block pin."""

    # instance attributes
    _parent : BlockItem
    _pin    : BlockPinItem

    @checked
    def __init__(
        self   : Self,
        view   : DiagramView,
        parent : BlockItem,
        pin    : BlockPinItem,
        pos    : QPointF,
        snap   : QPointF | None = None
    ) -> None:
        super().__init__(view)
        self._parent = parent
        self._pin = pin
        self.update(pos, snap)

    def valid(self : Self) -> bool:
        return \
            self._parent is not None and \
            hasattr(self, "_pin") and \
            self._pin is not None
