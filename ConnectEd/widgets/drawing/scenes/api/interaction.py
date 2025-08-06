from typing import Self, Optional
from abc import ABC, abstractmethod

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem

from pyTooling.Decorators import export

from .....core import paste

from ....dialogs.text       import TextDialog
from ....dialogs.text_block import TextBlockDialog

from ...items import ElementMixin, clone

from ...items.handle     import Handle

from ...items.base_rect  import BaseRectangle
from ...items.port_pin   import BasePin
from ...items.base_text  import BaseText
from ...items.pin_rect   import PinRect
from ...items.port_pin   import Port
from ...items.block      import Block
from ...items.port_pin   import BlockPin
from ...items.rectangle  import Rectangle
from ...items.text       import Text
from ...items.text_block import TextBlock

from .cmd   import cmdAdd, cmdDelete, cmdMove, \
                   cmdAddPin, cmdDeletePin, cmdMovePin

from .cmd.edit import cmdEditText, cmdEditPropertyText, cmdEditAppearance, \
                      cmdEditProperties

from .cmd.place import cmdPlacePort, cmdPlaceBlock, cmdPlaceRectangle, \
                       cmdPlaceText, cmdPlaceTextBlock, cmdPlaceBlockPin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


ElementType = ElementMixin | QGraphicsItem

@export
class Interaction(ABC):
    """Base for all interactions."""

    @abstractmethod
    def valid(self) -> bool: ...

    @abstractmethod
    def update(self, pos: QPointF) -> None: ...

    @abstractmethod
    def complete(self, pos: QPointF) -> bool: ...

    @abstractmethod
    def cancel(self) -> None: ...

class SceneInteraction(Interaction):
    """Base for all interactions that operate on a scene."""

    # instance attributes
    _scene        : "DrawingScene"

    def __init__(self, scene: "DrawingScene"):
        self._scene = scene

class SceneElementInteraction(SceneInteraction):
    """Base for all interactions that operate on a single scene element."""
    # instance attributes
    _element : ElementType

    def __init__(self, scene: "DrawingScene", element: ElementType):
        SceneInteraction.__init__(self, scene)
        self._element = element

    @property
    def valid(self) -> bool:
        return self._element is not None

class SceneElementsInteraction(SceneInteraction):
    """Base for all interactions that operate on one or morescene elements."""

    # instance attributes
    _elements : list[ElementType]

    def __init__(self, scene: "DrawingScene", elements: list[ElementType]):
        SceneInteraction.__init__(self, scene)
        self._elements = elements

    @property
    def valid(self) -> bool:
        return self._elements is not None

class PinInteraction(Interaction):
    """Base for all interactions that operate on a pin."""

    # class attributes
    _PIN : BasePin  # subclass to override with specific pin class

    # instance attributes
    _parent : PinRect
    _pin    : BasePin

    def __init__(self : Self, parent : PinRect, pos : QPointF):
        if isinstance(parent, PinRect):
            self._parent = parent
        else:
            self._parent = None

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

    def update(self, pos: QPointF):
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
    _selection : Optional[list[ElementType]]
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

@export
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

    def complete(self, pos: QPointF) -> bool:
        self._restorePos()  # restore initial positions
        self.update(pos)    # apply final offset
        # add pasted elements to scene
        self._scene.undo_stack.push(cmdAdd(
            self._scene, self._elements, self._selection
        ))
        return True

    def cancel(self) -> None:
        self._removeFromScene()   # remove preview elements
        self._restoreSelection()  # restore original selection

@export
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

@export
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
        SceneElementsInteraction.__init__(self, scene, elements)
        self._ipos     = pos
        self._cpos     = pos
        self._slide    = slide
        self._storePos()  # record initial positions

    def complete(self, pos: QPointF) -> bool:
        self._restorePos()  # restore initial positions
        # apply final offset
        self._scene.undo_stack.push(cmdMove(
            self._scene, self._elements, pos - self._ipos, self._slide
        ))
        return True

    def cancel(self) -> None:
        self._restorePos()  # restore initial positions

@export
class EditResizeInteraction(EditMoveInteraction):
    def __init__(
        self   : Self,
        scene  : "DrawingScene",
        handle : Handle,
        pos    : QPointF
    ) -> None:
        EditMoveInteraction.__init__(self, scene, [handle], pos, False)

class PlaceBaseInteraction(
    SelectionMixin,          # _preserveSelection, _restoreSelection
    SceneElementInteraction  # _scene, _element, valid
):
    """Base for all interactions that place a single element."""

    # class attributes
    _ELEMENT : ElementType  # subclass to override with element class

    def __init__(self : Self, scene : "DrawingScene", pos : QPointF):
        element = self._ELEMENT(pos)
        SceneElementInteraction.__init__(self, scene, element)
        self._preserveSelection()
        self._scene.clearSelection()
        self._scene.addItem(self._element)
        self._element.setSelected(True)

    def update(self, pos: QPointF):
        self._element.setPos(pos)

    def complete(self, pos: QPointF) -> bool:
        self.update(pos)
        self._scene.undo_stack.push(cmdAdd(
            self._scene, [self._element], self._selection
        ))
        return True

    def cancel(self) -> None:
        self._scene.removeItem(self._element)
        self._restoreSelection()

class PlaceBaseRectInteraction(PlaceBaseInteraction):
    """Base for all interactions that place a single rectangular element."""

    # instance attributes
    _element : BaseRectangle  # type hint specific to this interaction

    def update(self, pos: QPointF):
        self._element.setP2(pos)

class PlaceBasePinInteraction(PinInteraction):
    """Base for all interactions that place a pin."""

    def __init__(self : Self, parent : PinRect, pos : QPointF):
        self._parent = parent
        if isinstance(parent, PinRect):
            self._pin = self._PIN(parent)
            self._pin.setParentItem(parent)
            self.update(pos)
        else:
            self._pin = None

    def update(self : Self, pos : QPointF) -> None:
        self._pin.setLoc(self._parent.getLoc(pos))

    def complete(self : Self, pos : QPointF) -> bool:
        self.update(pos)
        self._scene.undo_stack.push(cmdAddPin(self._parent, self._pin))

    def cancel(self : Self) -> None:
        self._pin.setParentItem(None)

@export
class PlacePortInteraction(PlaceBaseInteraction):
    _ELEMENT = Port

@export
class PlaceBlockInteraction(PlaceBaseRectInteraction):
    _ELEMENT = Block

@export
class PlaceBlockPinInteraction(PlaceBasePinInteraction):
    _PIN = BlockPin
    _parent : Block
    _pin    : BlockPin

#@export
#class PlaceSymbolPinOp(PlacePinBaseOp):
#    _CMD = cmdPlaceSymbolPin

@export
class PlaceRectangleInteraction(PlaceBaseRectInteraction):
    _ELEMENT = Rectangle

@export
class PlaceTextInteraction(PlaceBaseInteraction):
    _ELEMENT = Text
    _DIALOG  = TextDialog

    def __init__(self : Self, scene : "DrawingScene", pos : QPointF):
        element : Text = self._ELEMENT(pos)
        dialog = self._DIALOG(element)
        if dialog.exec():
            text, appearance = dialog.getChoice()
            element.setText(text)
            element.quill.setPref(appearance)
            SceneElementInteraction.__init__(self, scene, element)
            self._preserveSelection()
            self._scene.clearSelection()
            self._scene.addItem(self._element)
            self._element.setSelected(True)
        else:
            self._element = None

@export
class PlaceTextBlockInteraction(PlaceTextInteraction):
    _ELEMENT = TextBlock
    _DIALOG  = TextBlockDialog
