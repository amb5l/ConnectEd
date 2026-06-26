from __future__ import annotations

from typing import Self

from .......core.check import checked

from .. import CmdSceneItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .....scenes.drawing        import DrawingScene
    from .....items.mixin.transform import ItemTransformMixin
    from .....items.mixin.handle    import ItemHandlesMixin


class CmdEditOrigin(CmdSceneItem):
    _item   : ItemTransformMixin | ItemHandlesMixin
    _before : str
    _after  : str

    @checked
    def __init__(
        self    : Self,
        scene   : DrawingScene,
        item    : ItemTransformMixin | ItemHandlesMixin,
        ap_name : str
    ) -> None:
        super().__init__(scene, item)
        self._before = item.origin()
        self._after = ap_name

    @checked
    def redo(self : Self) -> None:
        """Change origin without changing scene position."""
        self._item.setOrigin(self._after)

    @checked
    def undo(self : Self) -> None:
        """Change origin without changing scene position."""
        self._item.setOrigin(self._before)
