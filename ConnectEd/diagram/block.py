from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPen, QBrush

from prefs import prefs
from .common import ItemState, RectAnchorPoint
from .text import Property, PropertyVisibility


#-------------------------------------------------------------------------------

class BlockPropertyAnchor:
    def __init__(self, remote, local, offset):
        self.remote = remote
        self.local  = local
        self.offset = offset

#-------------------------------------------------------------------------------

class Block:
    def __init__(self, position, size, properties):
        self.rect        = QRectF(position, size)
        self.properties  = {}
        self.state       = ItemState.NORMAL
        self.highlighted = False
        n = 0
        # position properties on a newly created block
        for name, value in properties:
            if n == 0:
                blockAnchor    = RectAnchorPoint.TOP_LEFT
                propertyAnchor = RectAnchorPoint.BOTTOM_LEFT
                propertyOffset = QPointF(0,0)
            else:
                blockAnchor    = RectAnchorPoint.BOTTOM_LEFT
                propertyAnchor = RectAnchorPoint.TOP_LEFT
                propertyOffset = QPointF(0,10*(n-1))
            self.properties[name] = Property(
                self,
                name,
                value,
                BlockPropertyAnchor(
                    blockAnchor,
                    propertyAnchor,
                    propertyOffset
                ),
                0.0,
                PropertyVisibility.VALUE
            )
            n += 1

    def setRect(self, rect):
        self.rect = rect

    def setSize(self, size):
        self.rect.setSize(size)

    def setPosition(self, position):
        self.rect.moveTo(position)

    # detect if p hits this block or any of its child objects
    def select(self, p):
        # check child objects
        for _, property in self.properties.items():
            if property.select(p):
                return True
        # check block outline and fill
        w = prefs.dwg.block.line.width / 2
        o = QPointF(w, w)
        r = QRectF(self.rect.topLeft()  - o, self.rect.topRight() + o)
        if r.contains(p):
            self.state |= ItemState.SELECTED
        return True

    def draw(self, painter):
        if ItemState.MOVING in self.state:
            line = prefs.dwg.moving.line
            fill = prefs.dwg.moving.fill
        elif ItemState.HIGHLIGHTED in self.state:
            line = prefs.dwg.highlighted.line
            fill = prefs.dwg.highlighted.fill
        elif ItemState.SELECTED in self.state:
            line = prefs.dwg.selected.line
            fill = prefs.dwg.selected.fill
        else:
            line = prefs.dwg.block.line
            fill = prefs.dwg.block.fill
        pen = QPen(line.color, line.width, Qt.PenStyle.SolidLine)
        brush = QBrush(fill.color, fill.style)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRect(self.rect)
        # draw properties
        for _, p in self.properties.items():
            p.draw(painter)

#-------------------------------------------------------------------------------
