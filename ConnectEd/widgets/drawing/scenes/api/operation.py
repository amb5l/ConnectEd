from typing import Self
from abc import ABC, abstractmethod

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsItem

from pyTooling.Decorators import export

from .....core import logger, paste

from ...items import ElementMixin, Rectangle

from .cmd   import cmdBase
from .edit  import cmdEditPaste, cmdEditDuplicate, cmdEditMove
from .place import cmdPlaceBlock, cmdPlaceRectangle

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


ElementType = ElementMixin | QGraphicsItem

class Operation(ABC):
    """Base for all view-scene operations"""
    # instance attributes
    _scene : "DrawingScene"

    def __init__(self, scene: "DrawingScene"):
        self._scene = scene

    @abstractmethod
    def is_valid(self) -> bool: ...

class ImmediateOperation(Operation):
    """Operations that execute immediately"""
    @abstractmethod
    def execute(self, pos: QPointF) -> bool: ...

class InteractiveOperation(Operation):
    """Operations with begin → continue → complete cycle"""
    @abstractmethod
    def update(self, pos: QPointF) -> None: ...
    @abstractmethod
    def complete(self, pos: QPointF) -> bool: ...
    @abstractmethod
    def cancel(self) -> None: ...

@export
class EditCutOperation(ImmediateOperation):
    def __init__(self, scene):
        super().__init__(scene)

    def execute(self, pos: QPointF) -> bool:
        pass

@export
class EditCopyOperation(ImmediateOperation):
    def __init__(self, scene):
        super().__init__(scene)

    def execute(self, pos: QPointF) -> bool:
        pass

@export
class EditPasteOperation(InteractiveOperation):
    # instance attributes
    _elements : list[ElementType] # TODO kill this, put them in command
    _pos      : QPointF

    def __init__(self, scene, pos):
        super().__init__(scene)
        # Get paste data - this is the core operation logic
        elements, copy_pos = paste()
        self._elements = elements if elements else []
        self._pos = copy_pos if copy_pos else pos

        # Add elements to scene for preview
        if self._elements:
            for element in self._elements:
                if element.scene() != self._scene:
                    self._scene.addItem(element)
            self.update(pos)

    @property
    def is_valid(self) -> bool:
        return bool(self._elements)

    def update(self, pos: QPointF):
        """Update with current position for paste preview"""
        offset = pos - self._pos
        for element in self._elements:
            element.moveBy(offset)
        self._pos = pos

    def complete(self, pos: QPointF) -> bool:
        offset = pos - self._pos

        # Remove preview elements and reset position for command
        for element in self._elements:
            if element.scene() == self._scene:
                self._scene.removeItem(element)
            element.moveBy(-offset)

        # Create proper undo command
        paste_cmd = cmdEditPaste(
            self._scene, self._elements, offset
        )
        self._scene.undo_stack.push(paste_cmd)
        return True

    def cancel(self) -> None:
        self._revert()

    def _revert(self) -> None:
        for element in self._elements:
            if element.scene() == self._scene:
                self._scene.removeItem(element)

@export
class EditDeleteOperation(ImmediateOperation):
    def __init__(self, scene):
        super().__init__(scene)

    def execute(self, _: QPointF) -> bool:
        pass

@export
class EditDuplicateOperation(InteractiveOperation):
    # instance attributes
    _command      : cmdEditDuplicate
    _initial_pos  : QPointF
    _current_pos  : QPointF
    _initial_spos : dict[ElementType, QPointF] # initial element scene positions

    def __init__(
        self     : Self,
        scene    : "DrawingScene",
        pos      : QPointF
    ) -> None:
        super().__init__(scene)
        self._initial_pos = pos
        self._current_pos = pos
        originals = scene._selectedTopElements()
        self._command = cmdEditDuplicate(scene, originals)
        self._command.begin() # create clones and add them to the scene
        self._initial_spos = {e: e.scenePos() for e in self._command.elements}

    @property
    def is_valid(self) -> bool:
        return bool(self._elements)

    def update(self, pos: QPointF):
        self._moveBy(pos - self._current_pos)
        self._current_pos = pos

    def complete(self, pos: QPointF) -> bool:
        self._restorePos()
        self._moveBy(pos - self._initial_pos)
        self._scene.undo_stack.push(self._command)
        return True

    def cancel(self) -> None:
        self._command.cancel() # remove clones from scene, restore selection set

    def _moveBy(self, offset: QPointF) -> None:
        for element in self._command.elements:
            element.moveBy(offset)

    def _restorePos(self) -> None:
        for element in self._command.elements:
            element.moveBy(self._initial_spos[element] - element.scenePos())

@export
class EditMoveOperation(InteractiveOperation):
    # instance attributes
    _elements     : list[ElementType]
    _slide        : bool
    _initial_pos  : QPointF  # where the operation started
    _current_pos  : QPointF  # current position during updates
    _initial_spos : dict[ElementType, QPointF]  # initial element scene positions

    def __init__(self, scene, elements, pos, slide=False):
        super().__init__(scene)
        self._elements    = elements
        self._slide       = slide
        self._initial_pos = pos
        self._current_pos = pos
        self._initial_spos = {e: e.scenePos() for e in elements}

    def update(self, pos: QPointF):
        offset = pos - self._current_pos
        for element in self._elements:
            element.moveBy(offset)
        self._current_pos = pos

    def complete(self, pos: QPointF) -> bool:
        self._revert()
        offset = pos - self._initial_pos
        if offset != QPointF(0, 0):
            move_cmd = cmdEditMove(
                self._scene, self._elements, offset, self._slide
            )
            self._scene.undo_stack.push(move_cmd)
        return True

    def cancel(self) -> None:
        self._revert()

    @property
    def is_valid(self) -> bool:
        return bool(self._elements)

    def _revert(self) -> None:
        """Reset elements back to their exact initial positions"""
        for element in self._elements:
            element.moveBy(self._initial_spos[element] - element.scenePos())
        self._current_pos = self._initial_pos

class PlaceBaseOperation(InteractiveOperation):
    # class attributes
    _CMD : cmdBase

    # instance attributes
    _pos     : QPointF
    _command : cmdBase

    def __init__(self, scene, pos):
        super().__init__(scene)
        self._pos = pos
        self._command = self._CMD(scene)
        self._command.begin(pos)

    def complete(self, pos: QPointF) -> bool:
        self._scene.undo_stack.push(self._command)
        return True

    def cancel(self) -> None:
        self._command.cancel()

    @property
    def is_valid(self) -> bool:
        return self.element is not None

@export
class PlaceRectangleOperation(PlaceBaseOperation):
    # class attributes
    _CMD = cmdPlaceRectangle

    _command : cmdPlaceRectangle

    def update(self, pos: QPointF):
        self._command.element.setP2(pos)

@export
class PlacePortOperation(InteractiveOperation):
    # instance attributes
    port      : ElementType  # The preview port element
    name      : str
    direction : str
    range_val : str

    def __init__(self, scene, pos, name, direction, range_val):
        super().__init__(scene)
        self.name = name
        self.direction = direction
        self.range_val = range_val
        # TODO: Create preview port
        self.port = None  # scene._createPreviewPort(pos, name, direction, range_val)

    @property
    def is_valid(self) -> bool:
        return self.port is not None

    def update(self, pos: QPointF):
        """Update port position"""
        if self.port:
            self.port.setPos(pos)

    def complete(self, pos: QPointF) -> bool:
        # TODO: Implement PlacePortOperation.complete()
        logger.warning("PlacePortOperation.complete() not implemented")
        return False

    def cancel(self) -> None:
        # TODO: Remove preview port from scene
        pass

@export
class PlaceBlockOperation(InteractiveOperation):
    # instance attributes
    block : ElementMixin  # The preview block element
    p1    : QPointF       # Starting corner
    p2    : QPointF       # Current second corner

    def __init__(self, scene, pos):
        super().__init__(scene)
        self.p1 = pos
        self.p2 = pos  # Initialize to same position
        # Create preview block (assuming scene has a method for this)
        self.block = scene._createPreviewBlock(pos)  # Scene should implement this
        if self.block and self.block.scene() != scene:
            scene.addItem(self.block)

    @property
    def is_valid(self) -> bool:
        return self.block is not None

    def update(self, pos: QPointF):
        """Update with current position as second corner of rectangle"""
        self.p2 = pos
        if self.block:
            rect = QRectF(self.p1, pos).normalized()  # Ensure positive width/height
            self.block.setRect(rect)

    def complete(self, pos: QPointF) -> bool:
        # pos is the second corner of the rectangle

        # Remove preview block
        if self.block and self.block.scene() == self._scene:
            self._scene.removeItem(self.block)

        # Create proper place command
        place_cmd = cmdPlaceBlock(self._scene, self.p1, pos)
        self._scene.undo_stack.push(place_cmd)
        return True

    def cancel(self) -> None:
        # Remove preview block from scene
        if self.block and self.block.scene() == self._scene:
            self._scene.removeItem(self.block)
