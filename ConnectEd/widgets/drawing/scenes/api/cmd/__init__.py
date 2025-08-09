from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QUndoCommand


from ......core.utils import camel_to_proper

from ....items import EdgeLoc, ElementMixin

from ....items.port_pin import BasePin
from ....items.pin_rect import PinRect

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


ElementType = ElementMixin | QGraphicsItem

class cmdBase(QUndoCommand):
    """Base class for all commands."""

    def id(self : Self) -> int:
        """Return a unique ID for merging commands."""
        class_id = hash(self.__class__.__name__) & 0x7FFFFFFF
        return class_id

    def mergeWith(self : Self, _ : QUndoCommand) -> bool:
        """Merge this command with another identical command."""
        return False  # never merge (for now)

class cmdSceneBase(cmdBase):
    """Base class for all commands that work with a scene."""

    # instance attributes
    _scene     : "DrawingScene"

    def __init__(self : Self, scene : "DrawingScene"):
        text = camel_to_proper(self.__class__.__name__.replace("cmd", ""))
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

class cmdSceneElement(cmdSceneBase):
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

class cmdSceneElements(cmdSceneBase):
    """Base class for all commands that work with multiple elements."""

    # instance attributes
    _elements : list[ElementType]

    def __init__(
        self     : Self,
        scene    : "DrawingScene",
        elements : list[ElementType]
    ):
        super().__init__(scene)
        self._elements = elements

class cmdPinBase(cmdBase):
    """Base class for all commands that work with a pin."""

    # instance attributes
    _parent : PinRect
    _pin    : BasePin

    def __init__(
        self : Self,
        parent : PinRect,
        pin    : BasePin
    ):
        super().__init__()
        self._parent = parent
        self._pin = pin

class cmdSelectionMixin:
    """Mixin for commands that need to preserve/restore the scene selection."""

    # instance attributes
    _scene     : "DrawingScene"
    _selection : list[ElementType]

    def _preserveSelection(self : Self, selection : list[ElementType]) -> None:
        self._selection = selection.copy()

    def _restoreSelection(self : Self) -> None:
        self._scene.blockSignals(True)
        self._scene.clearSelection()
        for e in self._selection:
            e.setSelected(True)
        self._scene.blockSignals(False)
        self._scene.selectionChanged.emit()

class cmdAddRemoveMixin:
    """Mixin for commands that add/remove elements to/from the scene."""

    # instance attributes
    _scene    : "DrawingScene"
    _elements : list[ElementType]

    def _addToScene(self : Self, select : bool = True) -> None:
        self._scene.blockSignals(True)
        self._scene.clearSelection()
        for e in self._elements:
            if e.scene() != self._scene:
                self._scene.addItem(e)
            if select:
                e.setSelected(True)
        self._scene.blockSignals(False)
        self._scene.selectionChanged.emit()

    def _removeFromScene(self : Self) -> None:
        self._scene.blockSignals(True)
        for e in self._elements:
            if e.scene() == self._scene:
                self._scene.removeItem(e)
        self._scene.blockSignals(False)
        self._scene.selectionChanged.emit()

class cmdMoveMixin:
    """Mixin for commands that move elements by an offset."""

    # instance attributes
    _elements : list[ElementType]
    _spos     : dict[ElementMixin, QPointF]  # initial scene positions

    def _moveBy(self : Self, offset : QPointF) -> None:
        for e in self._elements:
            e.moveBy(offset)

    def _storePos(self) -> None:
        self._spos = {e: e.scenePos() for e in self._elements}

    def _restorePos(self) -> None:
        for e in self._elements:
            e.moveBy(self._spos[e] - e.scenePos())

class cmdAdd(
    cmdSceneElements,   # _scene, _elements, _selection
    cmdSelectionMixin,  # _preserveSelection, _restoreSelection
    cmdAddRemoveMixin   # _addToScene, _removeFromScene
):
    """Command to add scene elements (paste, duplicate, etc.)."""

    # class attributes
    _SELECTION = True  # preserve selection set

    def __init__(
        self      : Self,
        scene     : "DrawingScene",
        elements  : list[ElementType],
        selection : list[ElementType]
    ):
        super().__init__(scene, elements) # record scene, elements
        self._preserveSelection(selection)   # store selection set

    def redo(self) -> None:
        self._addToScene(select=True)

    def undo(self) -> None:
        self._removeFromScene()
        self._restoreSelection()

class cmdDelete(
    cmdSceneElements,   # _scene, _elements, _selection
    cmdSelectionMixin,  # _preserveSelection, _restoreSelection
    cmdAddRemoveMixin   # _addToScene, _removeFromScene
):
    """Command to delete scene elements (cut, delete)."""

    def __init__(
        self      : Self,
        scene     : "DrawingScene",
        elements  : list[ElementType],
        selection : list[ElementType]
    ):
        super().__init__(scene, elements) # record scene, elements
        self._preserveSelection(selection)   # store selection set

    def redo(self) -> None:
        """Delete the elements from the scene."""
        self._removeFromScene()

    def undo(self) -> None:
        self._addToScene()
        self._restoreSelection()

class cmdMove(
    cmdSceneElements, # _scene, _elements
    cmdMoveMixin      # _moveBy, _storePos, _restorePos
):
    """Command to move scene elements by an offset."""

    # instance attributes
    _offset : QPointF
    _slide  : bool     # true => retain connections, false => break connections

    def __init__(
        self     : Self,
        scene    : "DrawingScene",
        elements : list[ElementMixin],
        offset   : QPointF,
        slide    : bool = False
    ):
        super().__init__(scene, elements)
        self._offset = offset
        self._slide = slide
        self._storePos() # store initial positions

    def redo(self : Self) -> None:
        self._moveBy(self._offset)
        # TODO: add slide logic

    def undo(self : Self) -> None:
        self._restorePos()
        # TODO: add slide logic

class cmdAddPin(cmdPinBase):
    """Command to add a pin to a pin rect."""

    def redo(self : Self) -> None:
        self._pin.setParentItem(self._parent)

    def undo(self : Self) -> None:
        self._pin.setParentItem(None)

class cmdDeletePin(cmdPinBase):
    """Command to delete a pin from a pin rect."""

    def redo(self : Self) -> None:
        self._pin.setParentItem(None)

    def undo(self : Self) -> None:
        self._pin.setParentItem(self._parent)

class cmdMovePin(cmdPinBase):
    """Command to move a pin."""

    # instance attributes
    _old_loc : EdgeLoc
    _new_loc : EdgeLoc

    def __init__(
        self : Self,
        parent : PinRect,
        pin    : BasePin,
        loc    : EdgeLoc
    ):
        super().__init__(parent, pin)
        self._old_loc = self._pin.getLoc()
        self._new_loc = loc

    def redo(self : Self) -> None:
        self._pin.setLoc(self._new_loc)
