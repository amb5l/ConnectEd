from typing import Any, Optional
from abc import ABC, abstractmethod
from enum import Enum, auto

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsItem

from .....core import logger, paste

from ...items import ElementMixin, clone

from .edit  import cmdEditPaste, cmdEditMove
from .place import cmdPlaceBlock

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


ElementType = ElementMixin | QGraphicsItem

class BaseOperation(ABC):
    # instance attributes
    scene : "DrawingScene"

    def __init__(self, scene: "DrawingScene"):
        self.scene = scene

    @abstractmethod
    def update(self, pos: QPointF) -> None: ...

    @abstractmethod
    def complete(self, pos: QPointF) -> bool: ...

    @abstractmethod
    def cancel(self) -> None: ...

    @abstractmethod
    def is_valid(self) -> bool: ...

class EditMoveOperation(BaseOperation):
    # instance attributes
    elements     : list[ElementType]
    slide        : bool
    initial_pos  : QPointF  # where the operation started
    current_pos  : QPointF  # current position during updates
    initial_epos : dict[ElementType, QPointF]  # initial element positions

    def __init__(self, scene, elements, start_pos, slide=False):
        super().__init__(scene)
        self.elements    = elements
        self.slide       = slide
        self.initial_pos = start_pos
        self.current_pos = start_pos
        self.initial_epos = {e: e.pos() for e in elements}

    def update(self, pos: QPointF):
        offset = pos - self.current_pos
        for element in self.elements:
            element.moveBy(offset.x(), offset.y())
        self.current_pos = pos

    def complete(self, pos: QPointF) -> bool:
        self._revert()
        offset = pos - self.initial_pos
        if offset != QPointF(0, 0):
            move_cmd = cmdEditMove(
                self.scene, self.elements, offset, self.slide
            )
            self.scene.undo_stack.push(move_cmd)
        return True

    def cancel(self) -> None:
        self._revert()

    @property
    def is_valid(self) -> bool:
        return bool(self.elements)

    def _revert(self) -> None:
        """Reset elements back to their exact initial positions"""
        for element in self.elements:
            element.setPos(self.initial_epos[element])
        self.current_pos = self.initial_pos

class EditDuplicateOperation(BaseOperation):
    # instance attributes
    elements : list[ElementType]
    pos      : QPointF
    prev_sel : list[ElementType]

    def __init__(self, scene, elements, pos):
        super().__init__(scene)
        self.elements = clone(elements)
        self.pos      = pos
        # Capture current selection - operation's responsibility
        self.prev_sel = [item for item in scene.selectedItems() if isinstance(item, ElementMixin)]
        # Add cloned elements to scene for preview
        for element in self.elements:
            if element.scene() != self.scene:
                self.scene.addItem(element)
        self.update(pos)

    @property
    def is_valid(self) -> bool:
        return bool(self.elements)

    def update(self, pos: QPointF):
        """Update with current position for duplicate preview"""
        offset = pos - self.pos
        for element in self.elements:
            element.moveBy(offset.x(), offset.y())
        self.pos = pos

    def complete(self, pos: QPointF) -> bool:
        offset = pos - self.pos

        # Remove preview elements and reset position for command
        for element in self.elements:
            if element.scene() == self.scene:
                self.scene.removeItem(element)
            element.moveBy(-offset.x(), -offset.y())

        # Create proper undo command (reuse paste command for duplicates)
        duplicate_cmd = cmdEditPaste(self.scene, self.elements, offset, self.prev_sel)
        self.scene.undo_stack.push(duplicate_cmd)

        # Reset UUIDs for duplicated elements
        for element in self.elements:
            element.resetUuid()

        return True

    def cancel(self) -> None:
        # Remove preview elements from scene
        for element in self.elements:
            if element.scene() == self.scene:
                self.scene.removeItem(element)

class EditPasteOperation(BaseOperation):
    # instance attributes
    elements : list[ElementType]
    pos      : QPointF
    prev_sel : list[ElementType]

    def __init__(self, scene, pos):
        super().__init__(scene)
        # Get paste data - this is the core operation logic
        elements, copy_pos = paste()
        self.elements = elements if elements else []
        self.pos = copy_pos if copy_pos else pos
        # Capture current selection - operation's responsibility
        self.prev_sel = [item for item in scene.selectedItems() if isinstance(item, ElementMixin)]

        # Add elements to scene for preview
        if self.elements:
            for element in self.elements:
                if element.scene() != self.scene:
                    self.scene.addItem(element)
            self.update(pos)

    @property
    def is_valid(self) -> bool:
        return bool(self.elements)

    def update(self, pos: QPointF):
        """Update with current position for paste preview"""
        offset = pos - self.pos
        for element in self.elements:
            element.moveBy(offset.x(), offset.y())
        self.pos = pos

    def complete(self, pos: QPointF) -> bool:
        offset = pos - self.pos

        # Remove preview elements and reset position for command
        for element in self.elements:
            if element.scene() == self.scene:
                self.scene.removeItem(element)
            element.moveBy(-offset.x(), -offset.y())

        # Create proper undo command
        paste_cmd = cmdEditPaste(
            self.scene, self.elements, offset, self.prev_sel
        )
        self.scene.undo_stack.push(paste_cmd)
        return True

    def cancel(self) -> None:
        self._revert()

    def _revert(self) -> None:
        for element in self.elements:
            if element.scene() == self.scene:
                self.scene.removeItem(element)
        for element in self.prev_sel:
            self.scene.clearSelection()
            self.scene.setSelected(element, True)

class PlaceRectangleOperation(BaseOperation):
    # instance attributes
    rectangle : ElementType  # The preview rectangle element
    p1        : QPointF      # Starting corner
    p2        : QPointF      # Current second corner

    def __init__(self, scene, pos):
        super().__init__(scene)
        self.p1 = pos
        self.p2 = pos
        # TODO: Create preview rectangle
        self.rectangle = None  # scene._createPreviewRectangle(pos)

    @property
    def is_valid(self) -> bool:
        return self.rectangle is not None

    def update(self, pos: QPointF):
        """Update with current position as second corner of rectangle"""
        self.p2 = pos
        if self.rectangle:
            rect = QRectF(self.p1, pos).normalized()
            self.rectangle.setRect(rect)

    def complete(self, pos: QPointF) -> bool:
        # TODO: Implement PlaceRectangleOperation.complete()
        logger.warning("PlaceRectangleOperation.complete() not implemented")
        return False

    def cancel(self) -> None:
        # TODO: Remove preview rectangle from scene
        pass

class PlacePortOperation(BaseOperation):
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

class PlaceBlockOperation(BaseOperation):
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
        if self.block and self.block.scene() == self.scene:
            self.scene.removeItem(self.block)

        # Create proper place command
        place_cmd = cmdPlaceBlock(self.scene, self.p1, pos)
        self.scene.undo_stack.push(place_cmd)
        return True

    def cancel(self) -> None:
        # Remove preview block from scene
        if self.block and self.block.scene() == self.scene:
            self.scene.removeItem(self.block)

class OperationParams:
    """Type-safe parameter container for operations"""
    def __init__(self, **kwargs):
        self.data = kwargs

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

class OpType(Enum):
    EDIT_PASTE         = auto()
    EDIT_DUPLICATE     = auto()
    EDIT_MOVE          = auto()
    EDIT_SLIDE         = auto()
    EDIT_ASSIGN_ORIGIN = auto()
    PLACE_PORT         = auto()
    PLACE_BLOCK        = auto()
    PLACE_BLOCK_PIN    = auto()
    PLACE_RECTANGLE    = auto()
    PLACE_TEXT_BLOCK   = auto()
    PLACE_TEXT         = auto()

class DrawingSceneApiOperationMixin:
    def beginOperation(
        self    : "DrawingScene",
        op_type : OpType,
        pos     : QPointF,
        params  : Optional[OperationParams] = None
    ) -> Optional[BaseOperation]:
        """Single entry point for all interactive operations"""

        params = params or OperationParams()

        # Direct operation creation - no need for factory methods
        match op_type:
            case OpType.EDIT_PASTE:
                return EditPasteOperation(self, pos)

            case OpType.EDIT_DUPLICATE:
                elements = params.get('elements', self.selectedItems())
                if not elements:
                    return None
                return EditDuplicateOperation(self, elements, pos)

            case OpType.EDIT_MOVE:
                elements = params.get('elements', self.selectedItems())
                if not elements:
                    return None
                slide = params.get('slide', False)
                return EditMoveOperation(self, elements, pos, slide)

            case OpType.PLACE_BLOCK:
                return PlaceBlockOperation(self, pos)

            case OpType.PLACE_RECTANGLE:
                return PlaceRectangleOperation(self, pos)

            case OpType.PLACE_PORT:
                name = params.get('name')
                if not name:  # Require valid port name
                    return None
                direction = params.get('direction')
                range_val = params.get('range')
                return PlacePortOperation(self, pos, name, direction, range_val)

            case _:
                logger.error(f"Unknown operation type: {op_type}")
                return None
