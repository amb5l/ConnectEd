from __future__ import annotations

from typing import Self

from collections.abc import Callable

from PyQt6.QtCore import QPointF
from PyQt6.QtGui  import QUndoCommand

from ......core.check import checked
from ......core.utils import camel2proper

from ....items.segment import SegmentItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....items import ItemType
    from ....items.mixin import ItemMixin
    from .. import DrawingScene


class CmdBase(QUndoCommand):
    """Base class for all commands."""

    def id(self : Self) -> int:
        """Return a unique ID for merging commands."""
        class_id = hash(self.__class__.__name__) & 0x7FFFFFFF
        return class_id

    def mergeWith(self : Self, _ : QUndoCommand) -> bool:
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
    scene    : DrawingScene,
    cmd      : CmdBase,
    undoable : bool
) -> None:
    if undoable:
        scene.undo_stack.push(cmd)
    else:
        cmd.redo()


class CmdSceneBase(CmdBase):
    """Base class for all commands that work with a scene."""

    # instance attributes
    _scene : DrawingScene

    @checked
    def __init__(self : Self, scene : DrawingScene) -> None:
        text = camel2proper(self.__class__.__name__.replace("Cmd", ""))
        super().__init__(text)
        self._scene = scene


class CmdSceneItem(CmdSceneBase):
    """Base class for all commands that work with an item."""

    # instance attributes
    _item : ItemType

    @checked
    def __init__(
        self  : Self,
        scene : DrawingScene,
        item  : ItemType
    ) -> None:
        super().__init__(scene)
        self._item = item


class CmdSceneItems(CmdSceneBase):
    """Base class for all commands that work with multiple items."""

    # instance attributes
    _items : list[ItemType]

    @checked
    def __init__(
        self  : Self,
        scene : DrawingScene,
        items : list[ItemType]
    ) -> None:
        super().__init__(scene)
        self._items = items


class CmdAddRemoveMixin:
    """Mixin for commands that add/remove scene items."""

    # instance attributes
    _scene : DrawingScene
    _items : list[ItemType]

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
        scene : DrawingScene,
        items : list[ItemType]
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
        scene : DrawingScene,
        items : list[ItemType]
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
    _state  : dict[ItemMixin, QPointF]  # pre-move state (scene positions)

    @checked
    def __init__(
        self   : Self,
        scene  : DrawingScene,
        items  : list[ItemType],
        offset : QPointF
    ) -> None:
        super().__init__(scene, items)
        self._offset = offset
        self._state = {e: e.moveSave() for e in self._items}

    @checked
    def redo(self : Self) -> None:
        for e in self._items:
            if isinstance(e, SegmentItem):
                continue
            e.moveBy(self._offset)

    @checked
    def undo(self : Self) -> None:
        for e in self._items:
            if isinstance(e, SegmentItem):
                continue
            e.moveRestore(self._state[e])


class CmdRotateBase(CmdSceneItems):
    # class attributes
    _ROTATE   : Callable[[ItemType], None]
    _UNROTATE : Callable[[ItemType], None]
    _SIGN_X   : float
    _SIGN_Y   : float

    # instance attributes
    _pos    : QPointF | None          # individual if None, group otherwise
    _before : dict[ItemType, QPointF] # positions before

    @checked
    def __init__(
        self  : Self,
        scene : DrawingScene,
        items : list[ItemType],
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
                self._ROTATE(item)
        else:  # group rotation
            for item in self._items:
                self._ROTATE(item)
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
            self._UNROTATE(item)
            if self._pos is not None:
                item.setPos(self._before[item])


class CmdRotateCW(CmdRotateBase):
    @staticmethod
    def _ROTATE(item : ItemType) -> None:
        item.rotateCW()
    @staticmethod
    def _UNROTATE(item : ItemType) -> None:
        item.rotateCCW()
    _SIGN_X   = -1
    _SIGN_Y   = +1


class CmdRotateCCW(CmdRotateBase):
    @staticmethod
    def _ROTATE(item : ItemType) -> None:
        item.rotateCCW()
    @staticmethod
    def _UNROTATE(item : ItemType) -> None:
        item.rotateCW()
    _SIGN_X   = +1
    _SIGN_Y   = -1
