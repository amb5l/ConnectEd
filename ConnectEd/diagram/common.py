from PyQt6.QtCore import QPointF

from enum import Enum, Flag


class ItemState(Flag):
    NORMAL      = 0
    SELECTED    = 1
    HIGHLIGHTED = 2
    MOVING      = 4

class RectAnchorPoint(Enum):
    CENTER        = 0
    TOP_LEFT      = 1
    TOP_CENTER    = 2
    TOP_RIGHT     = 3
    RIGHT_CENTER  = 4
    BOTTOM_RIGHT  = 5
    BOTTOM_CENTER = 6
    BOTTOM_LEFT   = 7
    LEFT_CENTER   = 8

def getRectAnchorOffset(rect, anchor):
    match anchor:
        case RectAnchorPoint.TOP_LEFT:
            return QPointF(0,0)
        case RectAnchorPoint.TOP_CENTER:
            return QPointF(rect.width()/2, 0)
        case RectAnchorPoint.TOP_RIGHT:
            return QPointF(rect.width(), 0)
        case RectAnchorPoint.RIGHT_CENTER:
            return QPointF(rect.width(), rect.height()/2)
        case RectAnchorPoint.BOTTOM_RIGHT:
            return QPointF(rect.width(), rect.height())
        case RectAnchorPoint.BOTTOM_CENTER:
            return QPointF(rect.width()/2, rect.height())
        case RectAnchorPoint.BOTTOM_LEFT:
            return QPointF(0, rect.height())
        case RectAnchorPoint.LEFT_CENTER:
            return QPointF(0, rect.height()/2)
        case _:
            return QPointF(rect.width()/2, rect.height()/2)

def getRectAnchorPoint(rect, anchor):
    return QPointF(rect.topLeft()) + getRectAnchorOffset(rect, anchor)
