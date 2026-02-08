from enum import StrEnum


class HandleId(StrEnum):
    pass


class RectHandleId(HandleId):
    TOP_LEFT      = "Top Left"
    TOP_CENTER    = "Top Center"
    TOP_RIGHT     = "Top Right"
    MIDDLE_LEFT   = "Middle Left"
    MIDDLE_CENTER = "Middle Center"
    MIDDLE_RIGHT  = "Middle Right"
    BOTTOM_LEFT   = "Bottom Left"
    BOTTOM_CENTER = "Bottom Center"
    BOTTOM_RIGHT  = "Bottom Right"


class LineHandleId(HandleId):
    P1 = "P1"
    P2 = "P2"


class BlockPinHandleId(HandleId):
    ENTRY = "Entry"  # also placement origin
    NAME  = "Name"   # set just in from signal direction shape


class SymbolPinHandleId(HandleId):
    ORIGIN = "Origin"  # placement origin
    ENTRY  = "Entry"   # tip of external pin shape
    NAME   = "Name"    # set just in from placement origin
