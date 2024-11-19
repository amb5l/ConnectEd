from enum import Enum, Flag, auto
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPen, QBrush

from common import logger
from prefs.prefs import prefs
from diagram_item_property import ItemPropertyMixin


#-------------------------------------------------------------------------------
# base class for all diagram items

class Item:
    class State(Flag):
        NORMAL      = 0
        SELECTED    = 1
        HIGHLIGHTED = 2
        MOVING      = 4
        FIXED       = 8   # not movable, properties may be changed
        LOCKED      = 16  # not editable in any way

    # suitable for rectangular items
    # may need to change (and use subclasses) for other item shapes
    class AnchorPoint:
        '''
        Used to define the position of an anchor point on a rectangular item.
        '''
        CENTER        = 0
        TOP_LEFT      = 1
        TOP_CENTER    = 2
        TOP_RIGHT     = 3
        RIGHT_CENTER  = 4
        BOTTOM_RIGHT  = 5
        BOTTOM_CENTER = 6
        BOTTOM_LEFT   = 7
        LEFT_CENTER   = 8

    class Anchor:
        '''
        Used to define the position of an item relative to another item,
        using an anchor point at each end, and an offset.
        '''

        def __init__(self, remote, local, offset):
            '''
            Constructs a new instance.
            '''
            self.remote = remote
            self.local  = local
            self.offset = offset

    def __init__(self, type, pos):
        '''
        Constructs a new instance of the item.
        '''
        self.type         = type
        self.pos          = pos
        self.state        = self.State.NORMAL
        self.boundingRect = QRectF()

    def getType(self):
        return self.type

    #-------------------------------------------------------------------------------
    # selection support methods

    def selectBoundingRect(self, x):
        '''
        Determines if selection point or rectangle hits this instance.

        Args:
            x: QPointF or QRectF
        Returns:
            bool: True if hit, False otherwise
        '''
        if type(x) is QPointF:
            return self.boundingRect.contains(x)
        elif type(x) is QRectF:
            if prefs.edit.select.enclose:
                return x.contains(self.boundingRect)
            else:
                return x.intersects(self.boundingRect)
        else:
            logger.warning(f"Block.select: unsupported type = {type(x)}")

    #-------------------------------------------------------------------------------
    # paint support methods

    def penBrush(self, state, draw, theme, alpha=255):
        '''
        Returns pen and brush for this instance.
        '''
        lineWidth = draw.line.width
        fillStyle = draw.fill.style
        if self.State.MOVING in state:
            lineColor = theme.moving.line
            fillColor = theme.moving.fill
            lineWidth = 0
            fillStyle = Qt.BrushStyle.NoBrush
        elif self.State.HIGHLIGHTED in state:
            lineColor = theme.highlighted.line
            fillColor = theme.highlighted.fill
        elif self.State.SELECTED in state:
            lineColor = theme.selected.line
            fillColor = theme.selected.fill
        else:
            lineColor = theme.block.line
            fillColor = theme.block.fill
        lineColor.setAlpha(alpha)
        fillColor.setAlpha(alpha)
        pen = QPen(lineColor, lineWidth, Qt.PenStyle.SolidLine)
        brush = QBrush(fillColor, fillStyle)
        return pen, brush

#-------------------------------------------------------------------------------
# functional item class

class FunctionalItem(Item, ItemPropertyMixin):
    '''
    Base class for functional diagram items.
    '''
    class Type(Enum):
        TITLE    = auto()
        BLOCK    = auto()
        PIN      = auto()
        WIRE     = auto()
        TAP      = auto()
        JUNCTION = auto()
        PORT     = auto()
        CODE     = auto()

    def __init__(self, type, pos, properties):
        super().__init__(type, pos)
        if type(properties) is dict:
            # construct properties from dictionary
            n = 0
            for name, value in properties:
                if n == 0:
                    # first property is placed above item
                    itemAnchor = self.AnchorPoint.TOP_LEFT
                    propAnchor = self.AnchorPoint.BOTTOM_LEFT
                    propOffset = QPointF(0,0)
                else:
                    # subsequent properties are stacked below item
                    itemAnchor = self.AnchorPoint.BOTTOM_LEFT
                    propAnchor = self.AnchorPoint.TOP_LEFT
                    propOffset = QPointF(0,10*(n-1))
                if name not in self.properties:
                    self.properties[name] = self.Property(
                        self,
                        name,
                        value,
                        self.Anchor(itemAnchor, propAnchor, propOffset),
                        0.0,
                        self.Visibility.VALUE
                    )
                else:
                    logger.error(f'FunctionalItem: property name ({name}) already exists')
                n += 1
        else:
            self.properties = properties

    def isFunctional(self):
        return True



#-------------------------------------------------------------------------------
# decorative item class

class DecorativeItem(Item):
    '''
    Base class for decorative diagram items.
    '''
    class Type(Enum):
        LINE      = auto()
        RECTANGLE = auto()
        POLYGON   = auto()
        ARC       = auto()
        ELLIPSE   = auto()
        TEXTLINE  = auto()
        TEXTBOX   = auto()
        IMAGE     = auto()

    def isFunctional(self):
        return False
