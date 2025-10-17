from typing import Self

from .mixin.loc    import ElementLocMixin

from .port_pin import PortPinText, PortPinMixin
from .pin      import PinArrow, PinEntry, Pin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing import DrawingView


class BlockPinArrow(PinArrow):
    pass


class BlockPinEntry(PinEntry):
    pass


class BlockPinName(PortPinText):
    pass


class BlockPinComment(PortPinText):
    pass


class BlockPin(ElementLocMixin, Pin):
    # class attributes
    _PROPERTY_SPECS = \
        ElementLocMixin._PROPERTY_SPECS_LOC | \
        PortPinMixin._PROPERTY_SPECS

    @classmethod
    def _getArrowClass(cls) -> type[BlockPinArrow]:
        return BlockPinArrow

    @classmethod
    def _getEntryClass(cls) -> type[BlockPinEntry]:
        return BlockPinEntry

    @classmethod
    def _getNameClass(cls) -> type[BlockPinName]:
        return BlockPinName

    @classmethod
    def _getCommentClass(cls) -> type[BlockPinComment]:
        return BlockPinComment

    def getMenuItems(self : Self) -> list[str]:
        return ["Edit"]

    def ctxMenuEdit(
        self    : Self,
        _checked : bool,
        view    : "DrawingView"
    ) -> None:
        view.editBlockPin(self)
