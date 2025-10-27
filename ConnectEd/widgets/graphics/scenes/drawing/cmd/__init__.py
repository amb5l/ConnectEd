from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtGui     import QUndoCommand

from ......core.utils import camel2proper

from ....items import EdgeLoc, ItemMixin, ItemType

from ....items.block     import Block
from ....items.block_pin import BlockPin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
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


class CmdSceneBase(CmdBase):
    """Base class for all commands that work with a scene."""

    # instance attributes
    _scene : "DrawingScene"

    def __init__(self : Self, scene : "DrawingScene"):
        text = camel2proper(self.__class__.__name__.replace("cmd", ""))
        super().__init__(text)
        self._scene = scene

    def redo(self : Self) -> None:
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement redo"
        )

    def undo(self : Self) -> None:
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement redo"
        )


class CmdSceneItem(CmdSceneBase):
    """Base class for all commands that work with an item."""

    # instance attributes
    _item : ItemType

    def __init__(
        self  : Self,
        scene : "DrawingScene",
        item  : ItemType
    ):
        super().__init__(scene)
        self._item = item


class CmdSceneItems(CmdSceneBase):
    """Base class for all commands that work with multiple items."""

    # instance attributes
    _items : list[ItemType]

    def __init__(
        self  : Self,
        scene : "DrawingScene",
        items : list[ItemType]
    ):
        super().__init__(scene)
        self._items = items


class CmdBlockPinBase(CmdBase):
    """Base class for all commands that work with a pin."""

    # instance attributes
    _parent : Block
    _pin    : BlockPin

    def __init__(
        self : Self,
        parent : Block,
        pin    : BlockPin
    ):
        super().__init__()
        self._parent = parent
        self._pin = pin


class CmdBlockPinsBase(CmdBase):
    """Base class for all commands that work with multiple block pins."""

    # instance attributes
    _parent : Block
    _pins   : list[BlockPin]

    def __init__(
        self : Self,
        parent : Block,
        pins   : list[BlockPin]
    ):
        super().__init__()
        self._parent = parent
        self._pins = pins


class CmdSelectionMixin:
    """Mixin for commands that need to preserve/restore the scene selection."""

    # instance attributes
    _scene     : "DrawingScene"
    _selection : list[ItemType]

    def _preserveSelection(self : Self, selection : list[ItemType]) -> None:
        self._selection = selection.copy()

    def _restoreSelection(self : Self) -> None:
        self._scene.blockSignals(True)
        self._scene.clearSelection()
        for e in self._selection:
            e.setSelected(True)
        self._scene.blockSignals(False)
        self._scene.selectionChanged.emit()


class CmdAddRemoveMixin:
    """Mixin for commands that add/remove scene items."""

    # instance attributes
    _scene : "DrawingScene"
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


class CmdMoveMixin:
    """Mixin for commands that move items by an offset."""
    # TODO merge this into cmdMove?

    # instance attributes
    _items : list[ItemType]
    _spos  : dict[ItemMixin, QPointF]  # initial scene positions

    def _moveBy(self : Self, offset : QPointF) -> None:
        for e in self._items:
            e.moveBy(offset)

    def _storePos(self : Self) -> None:
        self._spos = {e: e.scenePos() for e in self._items}

    def _restorePos(self : Self) -> None:
        for e in self._items:
            e.moveBy(self._spos[e] - e.scenePos())


class CmdAdd(
    CmdSceneItems,      # _scene, _items, _selection
    CmdSelectionMixin,  # _preserveSelection, _restoreSelection
    CmdAddRemoveMixin   # _addToScene, _removeFromScene
):
    """Command to add scene items (paste, duplicate, etc.)."""

    # class attributes
    _SELECTION = True  # preserve selection set

    def __init__(
        self      : Self,
        scene     : "DrawingScene",
        items     : list[ItemType],
        selection : list[ItemType]
    ):
        super().__init__(scene, items)      # record scene, items
        self._preserveSelection(selection)  # store selection set

    def redo(self : Self) -> None:
        self._addToScene(select=True)

    def undo(self : Self) -> None:
        self._removeFromScene()
        self._restoreSelection()


class CmdDelete(
    CmdSceneItems,      # _scene, _items, _selection
    CmdSelectionMixin,  # _preserveSelection, _restoreSelection
    CmdAddRemoveMixin   # _addToScene, _removeFromScene
):
    """Command to delete scene items (cut, delete)."""

    def __init__(
        self      : Self,
        scene     : "DrawingScene",
        items     : list[ItemType],
        selection : list[ItemType]
    ):
        super().__init__(scene, items)      # record scene, items
        self._preserveSelection(selection)  # store selection set

    def redo(self : Self) -> None:
        """Delete the items from the scene."""
        self._removeFromScene()

    def undo(self : Self) -> None:
        self._addToScene()
        self._restoreSelection()


class CmdMove(
    CmdSceneItems,  # _scene, _items
    CmdMoveMixin    # _moveBy, _storePos, _restorePos
):
    """Command to move scene items by an offset."""

    # instance attributes
    _offset : QPointF
    _slide  : bool     # true => retain connections, false => break connections

    def __init__(
        self   : Self,
        scene  : "DrawingScene",
        items  : list[ItemType],
        offset : QPointF,
        slide  : bool = False
    ):
        super().__init__(scene, items)
        self._offset = offset
        self._slide = slide
        self._storePos() # store initial positions

    def redo(self : Self) -> None:
        self._moveBy(self._offset)
        # TODO: add slide logic

    def undo(self : Self) -> None:
        self._restorePos()
        # TODO: add slide logic


class CmdRotate(CmdSceneItems):

    # instance attributes
    _angle  : float
    _before : dict[ItemType, float] # angles before

    def __init__(
        self  : Self,
        scene : "DrawingScene",
        items : list[ItemType],
        angle : float
    ):
        super().__init__(scene, items)
        self._angle = angle
        self._before = {e: e.rotation() for e in self._items}

    def redo(self : Self) -> None:
        for e in self._items:
            e.setRotation(self._before[e] + self._angle)

    def undo(self : Self) -> None:
        for e in self._items:
            e.setRotation(self._before[e])


class CmdAddBlockPin(CmdBlockPinBase):
    """Command to add a pin to a pin rect."""

    def redo(self : Self) -> None:
        self._pin.setParentItem(self._parent)

    def undo(self : Self) -> None:
        self._pin.setParentItem(None)


class CmdDeleteBlockPin(CmdBlockPinBase):
    """Command to delete a pin from a pin rect."""

    def redo(self : Self) -> None:
        self._pin.setParentItem(None)

    def undo(self : Self) -> None:
        self._pin.setParentItem(self._parent)


class CmdMoveBlockPins(CmdBlockPinsBase):
    """Command to move multiple pins by an offset."""

    # instance attributes
    _after  : dict[BlockPin, EdgeLoc] # locations after
    _before : dict[BlockPin, EdgeLoc] # locations before

    def __init__(
        self   : Self,
        parent : Block,
        pins   : list[BlockPin],
        after  : dict[BlockPin, EdgeLoc],
        before : dict[BlockPin, EdgeLoc]
    ):
        super().__init__(parent, pins)
        self._after = after
        self._before = before

    def redo(self : Self) -> None:
        for pin in self._pins:
            pin.setLoc(self._after[pin])

    def undo(self : Self) -> None:
        for pin in self._pins:
            pin.setLoc(self._before[pin])
