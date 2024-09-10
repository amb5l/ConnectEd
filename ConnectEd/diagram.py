import xml.etree.ElementTree as ET
from PyQt6.QtCore import Qt, QRect, QRectF, QPoint, QPointF, QSize, QSizeF, pyqtSignal
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPen, QBrush
from enum import Enum

from app import prefs

#-------------------------------------------------------------------------------

# landscape sheet extents in inches x 100
EXTENTS_A4 = (1169, 827)
EXTENTS_A3 = (1654, 1169)
EXTENTS_A2 = (2338, 1654)
EXTENTS_A1 = (3307, 2338)
EXTENTS_A0 = (4677, 3307)
EXTENTS_A  = (970, 720)
EXTENTS_B  = (1520, 970)
EXTENTS_C  = (2020, 1520)
EXTENTS_D  = (3220, 2020)
EXTENTS_E  = (4220, 3220)

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

class PropertyVisibility(Enum):
    NONE  = 0
    VALUE = 1
    BOTH  = 2

#-------------------------------------------------------------------------------

# clickable QLabel
class InteractiveText(QLabel):
    def __init__(self,content):
        super().__init__(content)
        super().setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByKeyboard) # focus policy = Qt::ClickFocus
        self.mousePressed = False
        self.clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.mousePressed = True

    def mouseReleaseEvent(self, event):
        self.mousePressed = False
        self.clicked.emit()

    def leaveEvent(self, event):
        self.mousePressed = False
        return super().leaveEvent(event)

#-------------------------------------------------------------------------------

# InteractiveText with various attributes
class PropertyText(InteractiveText):
    def __init__(
        self,
        name,
        value,
        remoteAnchor,
        localAnchor,
        offset,
        rotation = 0.0,
        visibility=PropertyVisibility.VALUE
    ):
        match visibility:
            case PropertyVisibility.VALUE:
                text = value
            case PropertyVisibility.BOTH:
                text = name + "=" + value
            case _:
                text = ""
        super().__init__(text)
        self.remoteAnchor = remoteAnchor # RectAnchorPoint
        self.localAnchor  = localAnchor  # RectAnchorPoint
        self.offset       = offset       # QPointF
        self.rotation     = rotation     # int
        self.visibility   = visibility   # bool
        self.boundary     = None

    def draw(self, painter, remoteAnchorPoint, outline=False):
        if self.visibility == PropertyVisibility.NONE:
            return
        pen = QPen(prefs.dwg.block.propertyColor, 0.0, Qt.PenStyle.SolidLine)
        brush = QBrush(prefs.dwg.block.propertyColor)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.setFont(prefs.dwg.block.propertyFont)
        painter.save()
        flags = Qt.TextFlag.TextSingleLine
        if self.boundary == None:
            self.boundary = painter.boundingRect(QRect(0,0,1,1), flags, self.text())
        a = QPointF(0, 0) # adjust property position offset to account for property anchor point
        match self.localAnchor:
            case RectAnchorPoint.CENTER:
                a = QPointF(-self.boundary.width()/2, -self.boundary.height()/2)
            case RectAnchorPoint.TOP_LEFT:
                a = QPointF(0, 0)
            case RectAnchorPoint.TOP_CENTER:
                a = QPointF(-self.boundary.width()/2, 0)
            case RectAnchorPoint.TOP_RIGHT:
                a = QPointF(-self.boundary.width(), 0)
            case RectAnchorPoint.RIGHT_CENTER:
                a = QPointF(-self.boundary.width(), -self.boundary.height()/2)
            case RectAnchorPoint.BOTTOM_RIGHT:
                a = QPointF(-self.boundary.width(), -self.boundary.height())
            case RectAnchorPoint.BOTTOM_CENTER:
                a = QPointF(-self.boundary.width()/2, -self.boundary.height())
            case RectAnchorPoint.BOTTOM_LEFT:
                a = QPointF(0, -self.boundary.height())
            case RectAnchorPoint.LEFT_CENTER:
                a = QPointF(0, -self.boundary.height()/2)
        painter.translate(a)
        painter.rotate(self.rotation)
        painter.translate(remoteAnchorPoint + self.offset)
        painter.drawText(self.boundary, flags, self.text())
        brush.setStyle(Qt.BrushStyle.NoBrush)
        painter.setBrush(brush)
        if outline:
            painter.drawRect(self.boundary)
        painter.restore()

#-------------------------------------------------------------------------------

def getAnchorPoint(rect, anchor):
    match anchor:
        case RectAnchorPoint.TOP_LEFT:
            r = QPointF(rect.topLeft())
        case RectAnchorPoint.TOP_CENTER:
            r = QPointF(rect.topLeft())     + QPointF(rect.width()/2, 0)
        case RectAnchorPoint.TOP_RIGHT:
            r = QPointF(rect.topRight())
        case RectAnchorPoint.RIGHT_CENTER:
            r = QPointF(rect.topRight())    + QPointF(1, rect.height()/2)
        case RectAnchorPoint.BOTTOM_RIGHT:
            r = QPointF(rect.bottomRight())
        case RectAnchorPoint.BOTTOM_CENTER:
            r = QPointF(rect.bottomLeft())  + QPointF(rect.width()/2, 1)
        case RectAnchorPoint.BOTTOM_LEFT:
            r = QPointF(rect.bottomLeft())
        case RectAnchorPoint.LEFT_CENTER:
            r = QPointF(rect.topLeft())     + QPointF(0, rect.height()/2)
        case _:
            r = QPointF(rect.center())
    return r

#-------------------------------------------------------------------------------
# diagram object: block

class Block:
    def __init__(self, position, size, properties):
        self.rect       = QRectF(position, size)
        self.properties = {}
        self.highlight  = True
        n = 0
        for name, value in properties.items():
            if n == 0:
                blockAnchor = RectAnchorPoint.TOP_LEFT
                propAnchor  = RectAnchorPoint.BOTTOM_LEFT
                propOffset  = QPointF(0,0)
            else:
                blockAnchor = RectAnchorPoint.BOTTOM_LEFT
                propAnchor  = RectAnchorPoint.TOP_LEFT
                propOffset  = QPointF(0,10*(n-1))
            self.properties[name] = PropertyText(
                name,
                value,
                blockAnchor,
                propAnchor,
                propOffset,
                0.0,
                PropertyVisibility.BOTH
            )
            n += 1

    def set(self, rect):
        self.rect = rect

    def setSize(self, size):
        self.rect.setSize(size)

    def setPosition(self, position):
        self.rect.moveTo(position)

    def draw(self,painter):
        lineColor = prefs.dwg.color.select if self in diagram.selectionSet else \
                    prefs.dwg.color.highlight if self.highlight else \
                    prefs.dwg.block.lineColor
        pen = QPen(lineColor, prefs.dwg.block.lineWidth, Qt.PenStyle.SolidLine)
        if prefs.dwg.block.fillColor == None:
            brush = QBrush(Qt.BrushStyle.NoBrush)
        else:
            brush = QBrush(prefs.dwg.block.fillColor)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRect(self.rect)
        for _, v in self.properties.items():
            v.draw(painter, getAnchorPoint(self.rect, v.remoteAnchor), prefs.dwg.block.propertyOutline)

#-------------------------------------------------------------------------------

class Diagram:
    startPos = QPointF()
    def __init__(self,title):
        self.title         = title
        self.extents       = QSize(EXTENTS_A4[0], EXTENTS_A4[1])
        self.blocks        = []
        self.texts         = []
        self.selectionSet  = []
        self.selectionPos  = QPointF()
        self.selectionRect = None

    def selectionStart(self, pos):
        self.startPos      = pos
        self.selectionRect = QRectF(pos, pos + QPointF(1,1))

    def normalizeRect(self, p, s):
        if p.x() > s.x() and p.y() > s.y():                          # p is right and below s
            r = QRectF(s, p)
        elif p.x() > s.x() and p.y() <= s.y():                       # p is right and above s
            r = QRectF(QPointF(s.x(), p.y()), QPointF(p.x(), s.y()))
        elif p.x() <= s.x() and p.y() <= s.y():                      # p is left and above s
            r = QRectF(p, s)
        elif p.x() <= s.x() and p.y() > s.y():                       # p is left and below s
            r = QRectF(QPointF(p.x(), s.y()), QPointF(s.x(), p.y()))
        else:
            r = None
        return r
        # TODO: why not just
        # return QRectF(p, s) if p != s else None

    def selectionResize(self, p):
        if (r := self.normalizeRect(p, self.startPos)) is None:
             r = QRectF(p, QSize(1, 1))
        self.selectionRect = r

    def selectionEnd(self):
        # select all objects inside the selection rectangle
        self.selectionRect = None

    def selectionDraw(self, painter):
        if self.selectionRect is None:
            return
        pen = QPen(prefs.dwg.color.select, 0.0, Qt.PenStyle.DashDotLine)
        brush = QBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRect(self.selectionRect)

    def newBlockStart(self, pos):
        self.startPos = pos
        self.blocks.append(Block(
            pos,
            QSizeF(10, 10),
            {"reference": "ref?", "value": "val?"}
        ))

    def newBlockResize(self, p):
        n = self.blocks[-1] # last block in list = new block
        s = self.startPos
        if (r := self.normalizeRect(p, self.startPos)) is None:
            r = QRectF(s, QSizeF(10,10))
        n.set(r)

    def newBlockFinish(self):
        self.blocks[-1].highlight = False

    def newBlockCancel(self):
        self.blocks.pop()

    # return diagram object that was clicked on, or None
    def click(self, pos):
        for block in self.blocks:
            if QRectF(block.rect).contains(pos):
                return block
        return None

    def selectionClear(self):
        self.selectionSet = []

    def selectionAdd(self, object):
        if not object in self.selectionSet:
            self.selectionSet.append(object)

    def selectionTranslate(self, delta):
        for s in self.selectionSet:
            s.translate(delta)

    def draw(self, painter, visibleRect):
        # draw border
        if prefs.dwg.border.enable:
            pen = QPen(prefs.dwg.border.lineColor, prefs.dwg.border.lineWidth, Qt.PenStyle.SolidLine)
            brush = QBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(pen)
            painter.setBrush(brush)
            painter.drawRect(QRect(QPoint(0,0), self.extents-QSize(1,1)))
        # draw blocks
        pen = QPen(prefs.dwg.block.lineColor, prefs.dwg.block.lineWidth, Qt.PenStyle.SolidLine)
        if prefs.dwg.block.fillColor is None:
            brush = QBrush(Qt.BrushStyle.NoBrush)
        else:
            brush = QBrush(prefs.dwg.block.fillColor)
        painter.setPen(pen)
        painter.setBrush(brush)
        for block in self.blocks:
            if visibleRect.intersects(block.rect):
                block.draw(painter)
        # draw selection
        self.selectionDraw(painter)

    def load(self, filename):
        # create an ElementTree object from the XML file
        tree = ET.parse(filename)

        # get the root element
        root = tree.getroot()

        # get sub elements
        self.title = root.find("title").text
        self.sheetExtents = root.find("sheetExtents").text

    def save(self, filename):
        # create root element
        root = ET.Element("ConnectEd Diagram")

        # create sub elements
        ET.SubElement(root, "title").text = self.title
        ET.SubElement(root, "sheetExtents").text = self.sheetExtents

        # create an ElementTree object from the root element
        tree = ET.ElementTree(root)

        # write the XML tree to a file
        tree.write(filename, encoding="utf-8", xml_declaration=True)

#-------------------------------------------------------------------------------

untitledNumber = 1
diagram = Diagram("Untitled" + str(untitledNumber))
