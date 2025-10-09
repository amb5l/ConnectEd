from .port_pin import PortPinText

from .entry import Entry
from .pin   import PinArrow, Pin


class SymbolPinArrow(PinArrow):
    pass


class SymbolPinEntry(Entry):
    pass


class SymbolPinName(PortPinText):
    pass


class SymbolPinComment(PortPinText):
    pass


class SymbolPin(Pin):
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
