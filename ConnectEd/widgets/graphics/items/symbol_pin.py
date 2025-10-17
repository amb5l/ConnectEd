from .mixin.pos import ElementPosMixin

from .port_pin import PortPinText, PortPinMixin
from .pin      import PinArrow, Pin
from .entry    import Entry


class SymbolPinArrow(PinArrow):
    pass


class SymbolPinEntry(Entry):
    pass


class SymbolPinName(PortPinText):
    pass


class SymbolPinComment(PortPinText):
    pass


class SymbolPin(ElementPosMixin, Pin):
    # class attributes
    _PROPERTY_SPECS = \
        ElementPosMixin._PROPERTY_SPECS_POS | \
        PortPinMixin._PROPERTY_SPECS

    @classmethod
    def _getArrowClass(cls) -> type[SymbolPinArrow]:
        return SymbolPinArrow

    @classmethod
    def _getEntryClass(cls) -> type[SymbolPinEntry]:
        return SymbolPinEntry

    @classmethod
    def _getNameClass(cls) -> type[SymbolPinName]:
        return SymbolPinName

    @classmethod
    def _getCommentClass(cls) -> type[SymbolPinComment]:
        return SymbolPinComment
