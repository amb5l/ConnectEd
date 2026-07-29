from __future__ import annotations

from typing import Self, Any, TypeVar, Generic

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QUndoCommand

from ......core.check import checked
from ......core.utils import camel2proper

from ....items.grip    import GripItem
from ....items.segment import SegmentItem

from ....items.mixin import ItemMoveMixin

from ....items.mixin.transform import ItemTransformMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DiagramScene


class CmdBase(QUndoCommand):
    """Base class for all commands."""

    def id(self : Self) -> int:
        """Return a unique ID for merging commands."""
        class_id = hash(self.__class__.__name__) & 0x7FFFFFFF
        return class_id

    def mergeWith(self : Self, other : QUndoCommand | None) -> bool:
        """Merge this command with another identical command."""
        return False  # never merge (for now)

    def redo(self : Self) -> None:
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement redo"
        )

    def undo(self : Self) -> None:
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement redo"
        )


def cmdExec(
    scene    : DiagramScene,
    cmd      : CmdBase,
    undoable : bool
) -> None:
    if undoable:
        if (undo_stack := scene.undo_stack) is None:
            raise TypeError("No undo stack")
        undo_stack.push(cmd)
    else:
        cmd.redo()


class CmdSceneBase(CmdBase):
    """Base class for all commands that work with a scene."""

    # instance attributes
    _scene : DiagramScene

    @checked
    def __init__(self : Self, scene : DiagramScene) -> None:
        text = camel2proper(self.__class__.__name__.replace("Cmd", ""))
        super().__init__(text)
        self._scene = scene


TItem = TypeVar("TItem")


class CmdSceneItem(CmdSceneBase, Generic[TItem]):
    """Base class for all commands that work with an item."""

    # instance attributes
    _item : TItem

    @checked
    def __init__(
        self  : Self,
        scene : DiagramScene,
        item  : TItem
    ) -> None:
        super().__init__(scene)
        self._item = item


class CmdSceneItems(CmdSceneBase):
    """Base class for all commands that work with multiple items."""

    # instance attributes
    _items : list[QGraphicsItem]

    @checked
    def __init__(
        self  : Self,
        scene : DiagramScene,
        items : QGraphicsItem | list[QGraphicsItem]
    ) -> None:
        super().__init__(scene)
        if not isinstance(items, list):
            items = [items]
        self._items = items


class CmdAddRemoveMixin:
    """Mixin for commands that add/remove scene items."""

    # instance attributes
    _scene : DiagramScene
    _items : list[QGraphicsItem]

    def _addToScene(self : Self, select : bool = True) -> None:
        self._scene.blockSignals(True)
        self._scene.clearSelection()
        for e in self._items:
            if e.scene() != self._scene:
                self._scene.addItem(e)
            if select:
                e.setSelected(True)
        self._scene.blockSignals(False)
        self._scene.selectionChanged.emit()

    def _removeFromScene(self : Self) -> None:
        self._scene.blockSignals(True)
        for e in self._items:
            if e.scene() == self._scene:
                self._scene.removeItem(e)
        self._scene.blockSignals(False)
        self._scene.selectionChanged.emit()


class CmdAdd(
    CmdSceneItems,     # _scene, _items
    CmdAddRemoveMixin  # _addToScene, _removeFromScene
):
    """Command to add scene items (paste, duplicate, etc.)."""

    @checked
    def __init__(
        self  : Self,
        scene : DiagramScene,
        items : QGraphicsItem | list[QGraphicsItem]
    ) -> None:
        super().__init__(scene, items)      # record scene, items

    @checked
    def redo(self : Self) -> None:
        self._addToScene(select=True)

    @checked
    def undo(self : Self) -> None:
        self._removeFromScene()


class CmdDelete(
    CmdSceneItems,     # _scene, _items
    CmdAddRemoveMixin  # _addToScene, _removeFromScene
):
    """Command to delete scene items (cut, delete)."""

    @checked
    def __init__(
        self  : Self,
        scene : DiagramScene,
        items : list[QGraphicsItem]
    ) -> None:
        super().__init__(scene, items)      # record scene, items

    @checked
    def redo(self : Self) -> None:
        """Delete the items from the scene."""
        self._removeFromScene()

    @checked
    def undo(self : Self) -> None:
        self._addToScene(select=True)


class CmdMove(CmdSceneItems):
    """Command to move scene items by an offset."""

    # instance attributes
    _offset : QPointF
    _states : dict[QGraphicsItem, Any]  # pre-move state (scene positions)

    @checked
    def __init__(
        self   : Self,
        scene  : DiagramScene,
        items  : list[QGraphicsItem],
        offset : QPointF
    ) -> None:
        super().__init__(scene, items)
        self._offset = offset
        self._states = {
            item: item.moveSave()
            for item in self._items
            if isinstance(item, ItemMoveMixin)
        }

    @checked
    def redo(self : Self) -> None:
        for item in self._items:
            if isinstance(item, SegmentItem):
                continue
            if not isinstance(item, ItemMoveMixin):
                raise TypeError("Bad item")
            item.moveBy(self._offset.x(), self._offset.y())

    @checked
    def undo(self : Self) -> None:
        for item in self._items:
            if isinstance(item, SegmentItem):
                continue
            if not isinstance(item, ItemMoveMixin):
                raise TypeError("Bad item")
            item.moveRestore(self._states[item])


class CmdMoveGrip(CmdSceneItem[GripItem]):
    """Command to move a grip (handle edit via grip.moveBy → moveHandleBy)."""

    # instance attributes
    _offset : QPointF
    _state  : QPointF  # pre-move state from moveSave

    @checked
    def __init__(
        self   : Self,
        scene  : DiagramScene,
        grip   : GripItem,
        offset : QPointF
    ) -> None:
        if not grip.movable():
            raise TypeError("Grip is not movable")
        super().__init__(scene, grip)
        self._offset = offset
        self._state  = grip.moveSave()

    @checked
    def redo(self : Self) -> None:
        self._item.moveBy(self._offset.x(), self._offset.y())

    @checked
    def undo(self : Self) -> None:
        self._item.moveRestore(self._state)


class CmdRotateBase(CmdSceneItems):
    # class attributes
    _SIGN_X   : float
    _SIGN_Y   : float

    # instance attributes
    _pos    : QPointF | None                # individual if None, group otherwise
    _before : dict[QGraphicsItem, QPointF]  # positions before

    @checked
    def __init__(
        self  : Self,
        scene : DiagramScene,
        items : list[QGraphicsItem],
        pos   : QPointF | None = None
    ) -> None:
        super().__init__(scene, items)
        self._pos = pos
        if pos is not None:
            self._before = {item: item.pos() for item in self._items}

    @checked
    def redo(self : Self) -> None:
        if self._pos is None:  # individual rotation
            for item in self._items:
                self._rotate(item)
        else:  # group rotation
            for item in self._items:
                self._rotate(item)
                offset = item.pos() - self._pos
                offset_cw = QPointF(
                    self._SIGN_X * offset.y(),
                    self._SIGN_Y * offset.x()
                )
                new_pos = self._pos + offset_cw
                item.setPos(new_pos)

    @checked
    def undo(self : Self) -> None:
        for item in self._items:
            self._unrotate(item)
            if self._pos is not None:
                item.setPos(self._before[item])

    def _rotate(self : Self, item : QGraphicsItem) -> None:
        raise NotImplementedError("Subclass must implement _rotate")

    def _unrotate(self : Self, item : QGraphicsItem) -> None:
        raise NotImplementedError("Subclass must implement _unrotate")


class CmdRotateCW(CmdRotateBase):
    _SIGN_X   = -1
    _SIGN_Y   = +1

    def _rotate(self : Self, item : QGraphicsItem) -> None:
        if not isinstance(item, ItemTransformMixin):
            raise TypeError("Bad item")
        item.rotateCW()

    def _unrotate(self : Self, item : QGraphicsItem) -> None:
        if not isinstance(item, ItemTransformMixin):
            raise TypeError("Bad item")
        item.rotateCCW()


class CmdRotateCCW(CmdRotateBase):
    _SIGN_X   = +1
    _SIGN_Y   = -1

    def _rotate(self : Self, item : QGraphicsItem) -> None:
        if not isinstance(item, ItemTransformMixin):
            raise TypeError("Bad item")
        item.rotateCCW()

    def _unrotate(self : Self, item : QGraphicsItem) -> None:
        if not isinstance(item, ItemTransformMixin):
            raise TypeError("Bad item")
        item.rotateCW()
