from typing import Optional

from .....core import logger

from ...scenes.api.operation import OperationParams, OpType

from .state import DrawingViewStateBase

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingView


class DrawingViewOperationMixin:
    def _beginOperation(
        self    : "DrawingView",
        op_type : OpType,
        state   : DrawingViewStateBase,
        params  : Optional[OperationParams] = None
    ) -> None:
        """Generic operation begin pattern"""
        pos = self._snap(self.mouse.current.logical)
        operation = self.scene().beginOperation(op_type, pos, params)

        if not operation or not operation.is_valid:
            logger.warning(f"Failed to begin {op_type.name.lower()} operation")
            self.state.go(self.stateIdle)
            return

        self.wip.operation = operation
        self.wip.pos = pos
        self.state.go(state)

    def _continueOperation(self : "DrawingView") -> None:
        """Generic operation continue pattern"""
        if not self.wip.operation:
            logger.warning("No operation in progress")
            self.state.go(self.stateIdle)
            return

        new_pos = self._snap(self.mouse.current.logical)

        # Different operations use different update methods
        match self.wip.operation:
            case operation if hasattr(operation, 'update_position'):
                operation.update_position(new_pos)
            case operation if hasattr(operation, 'update_rect'):
                operation.update_rect(self.wip.pos, new_pos)
            case operation if hasattr(operation, 'update_movement'):
                offset = new_pos - self.wip.pos
                operation.update_movement(offset)

        self.wip.pos = new_pos

    def _completeOperation(self : "DrawingView", **commit_params) -> None:
        """Generic operation complete pattern"""
        if not self.wip.operation:
            logger.warning("No operation in progress")
            self.state.go(self.stateIdle)
            return

        final_pos = self._snap(self.mouse.current.logical)
        success = self.wip.operation.commit(pos=final_pos, **commit_params)

        self.wip.clear()
        self.state.go(self.stateIdle)
