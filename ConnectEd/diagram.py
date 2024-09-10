import sys
import xml.etree.ElementTree as ET
from PyQt6.QtCore import Qt, QRect, QPointF, pyqtSignal
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPen, QBrush, QColor
from enum import Enum

from app import prefs

#-------------------------------------------------------------------------------

# landscape sheet extents in inches x 100
SHEET_EXTENT_A4 = (1169, 827)
SHEET_EXTENT_A3 = (1654, 1169)
SHEET_EXTENT_A2 = (2338, 1654)
SHEET_EXTENT_A1 = (3307, 2338)
SHEET_EXTENT_A0 = (4677, 3307)
SHEET_EXTENT_A  = (970, 720)
SHEET_EXTENT_B  = (1520, 970)
SHEET_EXTENT_C  = (2020, 1520)
SHEET_EXTENT_D  = (3220, 2020)
SHEET_EXTENT_E  = (4220, 3220)

class RectAnchorPoint(Enum):
    CENTER       = 0
    TOPLEFT      = 1
    TOPCENTER    = 2
    TOPRIGHT     = 3
    RIGHTCENTER  = 4
    BOTTOMRIGHT  = 5
    BOTTOMCENTER = 6
    BOTTOMLEFT   = 7
    LEFTCENTER   = 8

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
            case RectAnchorPoint.TOPLEFT:
                a = QPointF(0, 0)
            case RectAnchorPoint.TOPCENTER:
                a = QPointF(-self.boundary.width()/2, 0)
            case RectAnchorPoint.TOPRIGHT:
                a = QPointF(-self.boundary.width(), 0)
            case RectAnchorPoint.RIGHTCENTER:
                a = QPointF(-self.boundary.width(), -self.boundary.height()/2)
            case RectAnchorPoint.BOTTOMRIGHT:
                a = QPointF(-self.boundary.width(), -self.boundary.height())
            case RectAnchorPoint.BOTTOMCENTER:
                a = QPointF(-self.boundary.width()/2, -self.boundary.height())
            case RectAnchorPoint.BOTTOMLEFT:
                a = QPointF(0, -self.boundary.height())
            case RectAnchorPoint.LEFTCENTER:
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
        case RectAnchorPoint.TOPLEFT:
            r = QPointF(rect.topLeft())
        case RectAnchorPoint.TOPCENTER:
            r = QPointF(rect.topLeft())     + QPointF(rect.width()/2, 0)
        case RectAnchorPoint.TOPRIGHT:
            r = QPointF(rect.topRight())    + QPointF(1, 0)
        case RectAnchorPoint.RIGHTCENTER:
            r = QPointF(rect.topRight())    + QPointF(1, rect.height()/2)
        case RectAnchorPoint.BOTTOMRIGHT:
            r = QPointF(rect.bottomRight()) + QPointF(1, 1)
        case RectAnchorPoint.BOTTOMCENTER:
            r = QPointF(rect.bottomLeft())  + QPointF(rect.width()/2, 1)
        case RectAnchorPoint.BOTTOMLEFT:
            r = QPointF(rect.bottomLeft())  + QPointF(0, 1)
        case RectAnchorPoint.LEFTCENTER:
            r = QPointF(rect.topLeft())     + QPointF(0, rect.height()/2)
        case _:
            r = QPointF(rect.center())
    return r

#-------------------------------------------------------------------------------

class Block:
    def __init__(self, position, size, properties):
        self.rect = QRect(position, size)
        self.properties = {}
        n = 0
        for name, value in properties.items():
            if n == 0:
                blockAnchor = RectAnchorPoint.TOPLEFT
                propAnchor  = RectAnchorPoint.BOTTOMLEFT
                propOffset  = QPointF(0,0)
            else:
                blockAnchor = RectAnchorPoint.BOTTOMLEFT
                propAnchor  = RectAnchorPoint.TOPLEFT
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

    def setSize(self, size):
        self.rect.setSize(size)

    def setPosition(self, position):
        self.rect.moveTo(position)

    def draw(self,painter):
        pen = QPen(prefs.dwg.block.lineColor, prefs.dwg.block.lineWidth, Qt.PenStyle.SolidLine)
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
    def __init__(self,title):
        self.title = title
        self.sheetExtents = SHEET_EXTENT_A4
        self.blocks = []
        self.texts = []

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