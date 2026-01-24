from typing import Self, Any

from PyQt6.QtCore import QPointF

from . import CmdSceneBase

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....scenes.drawing import DrawingScene
    from ....items.grip import GripItem


class CmdMoveGrip(CmdSceneBase):
    """
    Moving a grip works like moving an item in most cases,
    but text requires special handling because of the
    width and height constraints which can be "None".
    So let's use saveState and restoreState methods for Grips.
    """

    # instance attributes
    _grip   : "GripItem"
    _before : Any      # state to save e.g. pos and parent width/height
    _after  : Any      # state to restore e.g. pos and parent width/height
    _offset : QPointF  # movement offset

    def __init__(
        self   : Self,
        scene  : "DrawingScene",
        grip   : "GripItem",
        offset : QPointF
    ):
        super().__init__(scene)
        self._grip = grip

    def redo(self : Self) -> None:
        self._before = self._grip.saveState()
        self._grip.moveBy(self._delta)

    def undo(self : Self) -> None:
        self._grip.restoreState(self._before)
