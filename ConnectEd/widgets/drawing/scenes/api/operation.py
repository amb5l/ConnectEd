from typing import Any, Optional, Protocol
from abc import ABC, abstractmethod
from enum import Enum, auto

from PyQt6.QtCore import QPointF

from .....core import logger, paste

from ...items import ElementMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


class Operation(Protocol):
    """Generic interface for all interactive operations"""

    @property
    def is_valid(self) -> bool:
        """Check if operation has valid data"""
        ...

    @property
    def preview_elements(self) -> list[ElementMixin]:
        """Get elements for visual preview during interaction"""
        ...

    def update_pos(self, pos: QPointF) -> None:
        """Update for single-point operations (paste, duplicate, place text)"""
        ...

    def update_rect(self, p1: QPointF, p2: QPointF) -> None:
        """Update for rectangle operations (place block, place rectangle)"""
        ...

    def update_move(self, offset: QPointF, ortho: bool = False) -> None:
        """Update for movement operations (edit move)"""
        ...

    def commit(self, **params) -> bool:
        """Finalize the operation with undo command creation"""
        ...

    def cancel(self) -> None:
        """Cancel operation and clean up"""
        ...

class BaseOperation(ABC):
    """Base implementation with common functionality"""

    # instance attributes
    scene  : "DrawingScene"
    _macro : bool

    def __init__(self, scene: "DrawingScene"):
        self.scene  = scene
        self._macro = False

    def update_pos(self, pos: QPointF):
        logger.error(f"{self.__class__.__name__} does not support update_position")

    def update_rect(self, p1: QPointF, p2: QPointF) -> None:
        logger.error(f"{self.__class__.__name__} does not support update_rect")

    def update_move(self, offset: QPointF, ortho: bool = False) -> None:
        logger.error(f"{self.__class__.__name__} does not support update_movement")

    # Common functionality...
    def _begin_macro(self, description: str): ...
    def _end_macro(self): ...

    @abstractmethod
    def is_valid(self) -> bool: ...

    @abstractmethod
    def commit(self, **params) -> bool: ...

class EditMoveOperation(BaseOperation):
    def update_move(self, offset: QPointF):
        for element in self.elements:
            element.moveBy(offset.x(), offset.y())

class EditPasteOperation(BaseOperation):
    # instance attributes
    elements : list[ElementMixin]
    pos      : QPointF
    prev_sel : list[ElementMixin]

    def __init__(self, scene, elements, copy_pos, pos, prev_sel):
        super().__init__(scene)
        self.elements = elements
        self.pos      = copy_pos
        self.prev_sel = prev_sel
        self.update_pos(pos)

    def update_position(self, pos: QPointF):
        offset = pos - self.pos
        for element in self.elements:
            element.moveBy(offset.x(), offset.y())
        self.pos = pos

    @property
    def is_valid(self) -> bool:
        return bool(self.elements)

    @property
    def preview_elements(self) -> list[ElementMixin]:
        return self.elements

    def update_pos(self, pos: QPointF):
        offset = pos - self.pos
        for element in self.elements:
            element.moveBy(offset.x(), offset.y())
        self.pos = pos

    def commit(self, **params) -> bool:
        # Implementation...

    def cancel(self) -> None:
        # Implementation...

class PlaceBlockOperation(BaseOperation):
    def update_rect(self, p1: QPointF, p2: QPointF):
        self.block.setRect(QRectF(p1, p2))

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
    ) -> Optional[Operation]:
        """Single entry point for all interactive operations"""

        params = params or OperationParams()

        # Operation factory pattern
        match op_type:
            case OpType.EDIT_PASTE:
                return self._createPasteOperation(pos, params)

            case OpType.EDIT_DUPLICATE:
                elements = params.get('elements', self.selectedItems())
                return self._createDuplicateOperation(pos, elements, params)

            case OpType.EDIT_MOVE:
                elements = params.get('elements', self.selectedItems())
                slide = params.get('slide', False)
                return self._createMoveOperation(pos, elements, slide, params)

            case OpType.PLACE_BLOCK:
                return self._createPlaceBlockOperation(pos, params)

            case OpType.PLACE_RECTANGLE:
                return self._createPlaceRectangleOperation(pos, params)

            case OpType.PLACE_PORT:
                name = params.get('name')
                direction = params.get('direction')
                range_val = params.get('range')
                return self._createPlacePortOperation(pos, name, direction, range_val, params)

            case _:
                logger.error(f"Unknown operation type: {op_type}")
                return None

    def _createPasteOperation(
        self   : "DrawingScene",
        pos    : QPointF,
        params : OperationParams
    ) -> Optional[Operation]:
        elements, copy_pos = paste()
        if not elements:
            return None
        selection = self._selectedElements()
        return EditPasteOperation(self, elements, copy_pos, pos, selection)

    def _createPlaceBlockOperation(self, pos: QPointF, params: OperationParams) -> Operation:
        return PlaceBlockOperation(self, pos)