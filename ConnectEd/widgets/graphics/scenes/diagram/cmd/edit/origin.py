from __future__ import annotations

from typing import Self

from .......core.check import checked
from .......core.types import HandleId

from .....items.mixin.transform import ItemTransformMixin

from .. import CmdSceneItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .....scenes.diagram import DiagramScene


class CmdEditOrigin(CmdSceneItem[ItemTransformMixin]):
    _before : HandleId
    _after  : HandleId

    @checked
    def __init__(
        self   : Self,
        scene  : DiagramScene,
        item   : ItemTransformMixin,
        handle : HandleId
    ) -> None:
        super().__init__(scene, item)
        self._before = item.origin()
        self._after = handle

    @checked
    def redo(self : Self) -> None:
        """Change origin without changing scene position."""
        self._item.setOrigin(self._after)

    @checked
    def undo(self : Self) -> None:
        """Change origin without changing scene position."""
        self._item.setOrigin(self._before)
