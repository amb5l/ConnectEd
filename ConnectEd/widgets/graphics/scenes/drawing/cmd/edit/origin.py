from typing import Self

from .. import CmdSceneItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .....scenes.drawing      import DrawingScene
    from .....items.mixin.pos_rot import ItemPosRotMixin
    from .....items.mixin.handle  import ItemHandlesMixin


class CmdEditOrigin(CmdSceneItem):
    _item   : "ItemPosRotMixin | ItemHandlesMixin"
    _before : str
    _after  : str

    def __init__(
        self    : Self,
        scene   : "DrawingScene",
        item    : "ItemPosRotMixin | ItemHandlesMixin",
        ap_name : str
    ):
        super().__init__(scene, item)
        self._before = item.getOrigin()
        self._after = ap_name

    def redo(self : Self) -> None:
        """Change origin without changing scene position."""
        pos_before = self._item.getHandle(self._before).scenePos()
        pos_after = self._item.getHandle(self._after).scenePos()
        self._item.setOrigin(self._after)
        self._item.moveBy(pos_after - pos_before)

    def undo(self : Self) -> None:
        """Change origin without changing scene position."""
        pos_before = self._item.getHandle(self._before).scenePos()
        pos_after = self._item.getHandle(self._after).scenePos()
        self._item.setOrigin(self._before)
        self._item.moveBy(pos_before - pos_after)
