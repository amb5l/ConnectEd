from typing import Self, Optional
from abc import ABC, abstractmethod

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsItem

from pyTooling.Decorators import export

from .....core import logger, paste

from ...items import ElementMixin

from ...items.base_rect  import BaseRectangle
from ...items.port_pin   import Port
from ...items.text       import Text
from ...items.text_block import TextBlock

from .cmd   import cmdBase, cmdElements, cmdMoveMixin, cmdOffsetMixin
from .edit  import cmdEditPaste, cmdEditDuplicate, cmdEditMove
from .place import cmdPlacePort, cmdPlaceBlock, cmdPlaceRectangle, \
                   cmdPlaceText, cmdPlaceTextBlock

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


ElementType = ElementMixin | QGraphicsItem

class Operation:
    """Base for all view-scene operations"""
    _scene : "DrawingScene"

    def __init__(self, scene: "DrawingScene"):
        self._scene = scene

    @abstractmethod
    def is_valid(self) -> bool: ...

    @abstractmethod
    def update(self, pos: QPointF) -> None: ...

    @abstractmethod
    def complete(self, pos: QPointF) -> bool: ...

    @abstractmethod
    def cancel(self) -> None: ...

class CommandOperation(Operation):
    """Base class for command based operations."""

    # instance attributes
    _command : Optional[cmdBase]

    @property
    def is_valid(self) -> bool:
        return bool(self._command)

    def cancel(self) -> None:
        self._command.cancel()

class MoveOperationMixin:
    """Support for operations that move elements."""

    # instance attributes
    _scene        : "DrawingScene"
    _command      : cmdElements | cmdMoveMixin | cmdOffsetMixin
    _initial_pos  : QPointF
    _current_pos  : QPointF

    def update(self, pos: QPointF):
        self._command._moveBy(pos - self._current_pos)
        self._current_pos = pos

    def complete(self, pos: QPointF) -> bool:
        self._command._restorePos() # restore initial positions
        self._command.offset = pos - self._initial_pos # final offset
        self._scene.undo_stack.push(self._command)
        return True

@export
class EditPasteOperation(MoveOperationMixin, CommandOperation):
    def __init__(self, scene, pos):
        super().__init__(scene)
        elements, copy_pos = paste()
        if elements:
            self._initial_pos = pos if copy_pos is None else copy_pos
            self._current_pos = self._initial_pos
            self._command = cmdEditPaste(scene, elements)
            self._command.begin() # snapshot selection set
            self._storePos()  # store initial positions
            self.update(pos) # offset to specified position
        else:
            self._command = None

@export
class EditDuplicateOperation(MoveOperationMixin, CommandOperation):
    def __init__(
        self     : Self,
        scene    : "DrawingScene",
        pos      : QPointF
    ) -> None:
        super().__init__(scene)
        self._initial_pos = pos
        self._current_pos = pos
        originals = scene._selectedTopElements()
        if originals:
            self._command = cmdEditDuplicate(scene, originals)
            self._command.begin() # create clones and add them to the scene
            self._storePos()  # store initial positions
        else:
            self._command = None

@export
class EditMoveOperation(MoveOperationMixin, CommandOperation):
    # instance attributes
    _slide  : bool

    def __init__(
        self  : Self,
        scene : "DrawingScene",
        pos   : QPointF,
        slide : bool = False
    ) -> None:
        super().__init__(scene)
        self._initial_pos = pos
        self._current_pos = pos
        elements = scene._selectedTopElements()
        if elements:
            self._command = cmdEditMove(scene, elements, slide)
            self._command.begin()  # snapshot selection set
        else:
            self._command = None

    def update(self, pos: QPointF):
        super().update(pos)

class PlaceBaseOperation(CommandOperation):
    # class attributes
    _CMD : cmdBase

    # instance attributes
    _pos : QPointF

    def __init__(self, scene, pos):
        super().__init__(scene)
        self._pos = pos
        self._command = self._CMD(scene)
        self._command.begin(pos)

    def complete(self, pos: QPointF) -> bool:
        self._scene.undo_stack.push(self._command)
        return True

class PlaceBaseRectOperation(PlaceBaseOperation):
    def update(self, pos: QPointF):
        element : BaseRectangle = self._command.element
        element.setP2(pos)

@export
class PlacePortOperation(CommandOperation):
    _CMD = cmdPlacePort

    def update(self, pos: QPointF):
        element : Port = self._command.element
        element.setPos(pos)

@export
class PlaceBlockOperation(PlaceBaseRectOperation):
    _CMD = cmdPlaceBlock

@export
class PlaceRectangleOperation(PlaceBaseRectOperation):
    _CMD = cmdPlaceRectangle

@export
class PlaceTextOperation(PlaceBaseOperation):
    _CMD = cmdPlaceText

    def update(self, pos: QPointF):
        element : BaseText = self._command.element
        element.setPos(pos)
