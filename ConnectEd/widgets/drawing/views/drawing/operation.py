from typing import Optional

from .....core import logger

from ...scenes import DrawingScene

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
        scene : DrawingScene = self.scene()
        pos = self._snap(self.mouse.current.logical)
        operation = scene.beginOperation(op_type, pos, params)
        if not operation or not operation.is_valid:
            logger.warning(f"Failed to begin {op_type.name.lower()} operation")
            self.state.go(self.stateIdle)
            return
        self.operation = operation
        self.state.go(state)

    def _continueOperation(self : "DrawingView") -> None:
        if not self.operation:
            logger.warning("No operation in progress")
            self.state.go(self.stateIdle)
            return
        self.operation.update(self._snap(self.mouse.current.logical))

    def _completeOperation(self : "DrawingView", **commit_params) -> None:
        if not self.operation:
            logger.warning("No operation in progress")
            self.state.go(self.stateIdle)
            return
        self.operation.complete(self._snap(self.mouse.current.logical))
        self.operation = None
        self.state.go(self.stateIdle)
