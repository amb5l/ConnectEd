from PyQt6.QtCore import QPointF, QRectF

from enum import Enum, Flag


class DiagramCommonMixin:




    def getRectAnchorOffset(self, rect, anchor):
        match anchor:
            case self.RectAnchorPoint.TOP_LEFT:
                return QPointF(0,0)
            case self.RectAnchorPoint.TOP_CENTER:
                return QPointF(rect.width()/2, 0)
            case self.RectAnchorPoint.TOP_RIGHT:
                return QPointF(rect.width(), 0)
            case self.RectAnchorPoint.RIGHT_CENTER:
                return QPointF(rect.width(), rect.height()/2)
            case self.RectAnchorPoint.BOTTOM_RIGHT:
                return QPointF(rect.width(), rect.height())
            case self.RectAnchorPoint.BOTTOM_CENTER:
                return QPointF(rect.width()/2, rect.height())
            case self.RectAnchorPoint.BOTTOM_LEFT:
                return QPointF(0, rect.height())
            case self.RectAnchorPoint.LEFT_CENTER:
                return QPointF(0, rect.height()/2)
            case _:
                return QPointF(rect.width()/2, rect.height()/2)

    def getRectAnchorPoint(self, rect, anchor):
        return QPointF(rect.topLeft()) + self.getRectAnchorOffset(rect, anchor)

    #def normalizeRect(self, p, s):
    #    if p.x() > s.x() and p.y() > s.y():                          # p is right and below s
    #        r = QRectF(s, p)
    #    elif p.x() > s.x() and p.y() <= s.y():                       # p is right and above s
    #        r = QRectF(QPointF(s.x(), p.y()), QPointF(p.x(), s.y()))
    #    elif p.x() <= s.x() and p.y() <= s.y():                      # p is left and above s
    #        r = QRectF(p, s)
    #    elif p.x() <= s.x() and p.y() > s.y():                       # p is left and below s
    #        r = QRectF(QPointF(p.x(), s.y()), QPointF(s.x(), p.y()))
    #    else:
    #        r = None
    #    if r.width() < 10:
    #        r.setWidth(10)
    #    if r.height() < 10:
    #        r.setHeight(10)
    #    return r
    #    # TODO: why not just
    #    # return QRectF(p, s) if p != s else None
