from typing import Self
from abc import ABC, abstractmethod

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem

from .....core.xml import paste

from ...items import EdgeLoc, ElementMixin, clone

from ...items.base_rect  import BaseRectangle
from ...items.pin_rect   import PinRect
from ...items.block      import Block
from ...items.rectangle  import Rectangle
from ...items.text       import Text
from ...items.text_block import TextBlock
from ...items.port       import Port
from ...items.pin        import Pin
from ...items.block_pin  import BlockPin

from .cmd   import cmdAdd, cmdMove, cmdAddPin, cmdMovePins

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingScene


ElementType = ElementMixin | QGraphicsItem


class Interaction(ABC):
    """Base for all interactions."""

    # instance attributes
    _scene        : "DrawingScene"

    def __init__(self : Self, scene: "DrawingScene"):
        self._scene = scene

    @abstractmethod
    def valid(self : Self) -> bool: ...

    @abstractmethod
    def update(self : Self, pos: QPointF) -> None: ...

    @abstractmethod
    def complete(self : Self, pos: QPointF) -> bool: ...

    @abstractmethod
    def cancel(self : Self) -> None: ...


class SceneElementInteraction(Interaction):
    """Base for all interactions that operate on a single scene element."""
    # instance attributes
    _element : ElementType

    def __init__(self : Self, scene: "DrawingScene", element: ElementType):
        Interaction.__init__(self, scene)
        self._element = element

    @property
    def valid(self : Self) -> bool:
        return self._element is not None


class SceneElementsInteraction(Interaction):
    """Base for all interactions that operate on one or more scene elements."""

    # instance attributes
    _elements : list[ElementType]

    def __init__(self : Self, scene: "DrawingScene", elements: list[ElementType]):
        Interaction.__init__(self, scene)
        self._elements = elements

    @property
    def valid(self : Self) -> bool:
        return self._elements is not None


class PinInteraction(Interaction):
    """Base for all interactions that operate on a pin."""

    # class attributes
    _PIN : Pin  # subclass to override with specific pin class

    # instance attributes
    _parent : PinRect
    _pin    : Pin

    def __init__(
        self   : Self,
        scene  : "DrawingScene",
        parent : PinRect,
        pin    : Pin | None,
        pos    : QPointF,
        snap   : QPointF | None = None
    ) -> None:
        Interaction.__init__(self, scene)
        if isinstance(parent, PinRect):
            self._parent = parent
            self._pin = pin or self._PIN(parent)
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

    def update(self : Self, pos: QPointF):
        self._moveBy(pos - self._cpos)
        self._cpos = pos

    def _moveBy(self : Self, offset: QPointF) -> None:
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


class EditPasteInteraction(
    MoveMixin,                 # update, _moveBy, _storePos, _restorePos
    AddRemoveMixin,            # _addToScene, _removeFromScene
    SelectionMixin,            # _preserveSelection, _restoreSelection
    SceneElementsInteraction   # _scene, _elements, valid
):
    def __init__(
        self  : Self,
        scene : "DrawingScene",
        pos   : QPointF
    ) -> None:
        elements, copy_pos = paste()
        if elements:
            SceneElementsInteraction.__init__(self, scene, elements)
            self._ipos = pos if copy_pos is None else copy_pos
            self._cpos = self._ipos
            self._preserveSelection()  # store prior selection set
            self._elements = elements
            self._storePos()
            self._addToScene(select=True)
            self.update(pos)  # Move to initial position
        else:
            self._elements = None

    def complete(self : Self, pos: QPointF) -> bool:
        self._restorePos()  # restore initial positions
        self.update(pos)    # apply final offset
        # add pasted elements to scene
        self._scene.undo_stack.push(cmdAdd(
            self._scene, self._elements, self._selection
        ))
        return True

    def cancel(self : Self) -> None:
        self._removeFromScene()   # remove preview elements
        self._restoreSelection()  # restore original selection


class EditDuplicateInteraction(EditPasteInteraction):
    """Very similar to paste, but elements come from cloning."""

    def __init__(
        self     : Self,
        scene    : "DrawingScene",
        elements : list[ElementType],  # elements to duplicate
        pos      : QPointF             # duplication origin
    ) -> None:
        if elements:
            SceneElementsInteraction.__init__(self, scene, clone(elements))
            self._ipos = pos
            self._cpos = pos
            self._preserveSelection()  # store prior selection set
            self._storePos()
            self._addToScene(select=True)
        else:
            self._elements = None


class EditMoveInteraction(
    MoveMixin,                 # update, _moveBy, _storePos, _restorePos
    SceneElementsInteraction,  # _scene, _elements, valid
):
    # instance attributes
    _slide  : bool  # true => retain connections, false => break connections

    def __init__(
        self     : Self,
        scene    : "DrawingScene",
        elements : list[ElementType],
        pos      : QPointF,
        slide    : bool = False
    ) -> None:
        elements = elements if isinstance(elements, list) else [elements]
        SceneElementsInteraction.__init__(self, scene, elements)
        self._ipos     = pos
        self._cpos     = pos
        self._slide    = slide
        self._storePos()  # record initial positions

    def complete(self : Self, pos: QPointF) -> bool:
        self._restorePos()  # restore initial positions
        # apply final offset
        self._scene.undo_stack.push(cmdMove(
            self._scene, self._elements, pos - self._ipos, self._slide
        ))
        return True

    def cancel(self : Self) -> None:
        self._restorePos()  # restore initial positions


class EditMovePinsInteraction(Interaction):
    # instance attributes
    _parent : PinRect
    _pins   : list[Pin]                   # first element is primary pin
    _sloc   : dict[ElementType, EdgeLoc]  # stored locations of all pins

    def __init__(
        self   : Self,
        scene  : "DrawingScene",
        parent : PinRect,
        pins   : list[Pin]
    ) -> None:
        Interaction.__init__(self, scene)
        self._parent = parent
        self._pins = pins
        self._storeLoc()

    @property
    def valid(self : Self) -> bool:
        return \
            self._parent is not None and \
            hasattr(self, "_pins") and \
            len(self._pins) > 0

    def update(self : Self, pos: QPointF, snap: QPointF | None = None) -> None:
        pos_snap = self._scene._snap(pos, snap) if snap else pos
        primary = self._pins[0]
        loc_old = primary.loc()
        loc_new = self._parent.pos2loc(pos)
        loc_new_snap = self._parent.pos2loc(pos_snap)
        offset = self._parent.locDelta(loc_old, loc_new_snap)
        snap_pressure = self._parent.locDelta(loc_new, loc_new_snap)
        corner = +1 if snap_pressure > 0 else -1 if snap_pressure < 0 else 0
        self._pins[0].setLoc(loc_new_snap)
        for pin in self._pins[1:]:
            pin.setLoc(self._parent.locOffset(pin.loc(), offset, corner))

    def complete(self : Self, pos: QPointF, snap: QPointF | None = None) -> bool:
        self._restoreLoc()
        self.update(pos, snap)
        if all(p.loc() == self._sloc[p] for p in self._pins):
            return False # no change
        self._scene.undo_stack.push(cmdMovePins(
            self._parent,
            self._pins,
            {p: p.loc() for p in self._pins},
            self._sloc
        ))
        return True

    def cancel(self : Self) -> None:
        self._restoreLoc()

    def _storeLoc(self : Self) -> None:
        self._sloc = {p: p.loc() for p in self._pins}

    def _restoreLoc(self : Self) -> None:
        for p in self._pins:
            p.setLoc(self._sloc[p])


class PlaceBaseInteraction(
    SelectionMixin,          # _preserveSelection, _restoreSelection
    SceneElementInteraction  # _scene, _element, valid
):
    """Base for all interactions that place a single element."""

    # class attributes
    _ELEMENT : ElementType  # subclass to override with element class

    def __init__(
        self    : Self,
        scene   : "DrawingScene",
        pos     : QPointF,
        element : ElementType | None = None
    ) -> None:
        if element is None:
            element = self._ELEMENT(pos)
        else:
            element.setPos(pos)
        SceneElementInteraction.__init__(self, scene, element)
        self._preserveSelection()
        self._scene.clearSelection()
        self._scene.addItem(self._element)
        self._element.setSelected(True)

    def update(self : Self, pos: QPointF):
        self._element.setPos(pos)

    def complete(self : Self, pos: QPointF) -> bool:
        self.update(pos)
        self._scene.undo_stack.push(cmdAdd(
            self._scene, [self._element], self._selection
        ))
        return True

    def cancel(self : Self) -> None:
        self._scene.removeItem(self._element)
        self._restoreSelection()


class PlaceBaseRectInteraction(PlaceBaseInteraction):
    """Base for all interactions that place a single rectangular element."""

    # instance attributes
    _element : BaseRectangle  # type hint specific to this interaction

    def update(self : Self, pos: QPointF):
        self._element.setP2(pos)


class PlacePinInteraction(PinInteraction):
    """Base for all interactions that place a pin."""

    def __init__(
        self   : Self,
        scene  : "DrawingScene",
        parent : PinRect,
        pin    : Pin,
        pos    : QPointF,
        snap   : QPointF | None = None
    ) -> None:
        PinInteraction.__init__(self, scene, parent, pin, pos, snap)

    def update(self : Self, pos : QPointF, snap : QPointF | None = None) -> None:
        self._pin.setLoc(self._pin.locSnap(self._parent.pos2loc(pos), snap))

    def complete(self : Self, pos : QPointF, snap : QPointF | None = None) -> bool:
        self.update(pos, snap)
        self._scene.undo_stack.push(cmdAddPin(self._parent, self._pin))
        return True

    def cancel(self : Self) -> None:
        self._pin.setParentItem(None)


class PlacePortInteraction(PlaceBaseInteraction):
    _ELEMENT = Port


class PlaceBlockInteraction(PlaceBaseRectInteraction):
    _ELEMENT = Block


class PlaceBlockPinInteraction(PlacePinInteraction):
    _PIN = BlockPin


class PlaceRectangleInteraction(PlaceBaseRectInteraction):
    _ELEMENT = Rectangle


class PlaceTextInteraction(PlaceBaseInteraction):
    _ELEMENT = Text


class PlaceTextBlockInteraction(PlaceBaseInteraction):
    _ELEMENT = TextBlock
