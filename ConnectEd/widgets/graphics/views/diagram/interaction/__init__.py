from typing import Self

from PyQt6.QtCore import QPointF

from ......core.check import checked

from ....items.block     import BlockItem
from ....items.block_pin import BlockPinItem

from ...drawing.interaction import Interaction

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DiagramView


class BlockPinInteraction(Interaction):
    """Base for all interactions that operate on a block pin."""

    # instance attributes
    _parent : BlockItem | None
    _pin    : BlockPinItem | None

    @checked
    def __init__(
        self   : Self,
        view   : "DiagramView",
        parent : BlockItem | None,
        pin    : BlockPinItem | None,
        pos    : QPointF,
        snap   : QPointF | None = None
    ) -> None:
        super().__init__(view)
        if isinstance(parent, BlockItem):
            self._parent = parent
            self._pin = pin or BlockPinItem(parent)
            self._pin.setParentItem(parent)
            self.update(pos, snap)
        else:
            self._parent = None
            self._pin = None

    def valid(self : Self) -> bool:
        return \
            self._parent is not None and \
            hasattr(self, "_pin") and \
            self._pin is not None
