import xml.etree.ElementTree as ET
from PyQt6.QtCore import Qt, QRect, QRectF, QPoint, QPointF, QSize, QSizeF

from PyQt6.QtGui import QPen, QBrush
from enum import Enum, Flag, auto

from prefs import prefs
from .common import ItemState
from .block import Block

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

#-------------------------------------------------------------------------------

# TODO paste buffer

#-------------------------------------------------------------------------------

class Diagram:
    startPos = QPointF()
    def __init__(self,title):
        self.title         = title
        self.extents       = QSize(EXTENTS_A4[0], EXTENTS_A4[1])
        self.content       = []
        self.pasteBuffer   = []
        self.selectionSet  = []
        self.selectionPos  = QPointF()
        self.selectionRect = None

    # TODO minimum rectangle size
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
        if r.width() < 10:
            r.setWidth(10)
        if r.height() < 10:
            r.setHeight(10)
        return r
        # TODO: why not just
        # return QRectF(p, s) if p != s else None

    def selectionClear(self):
        self.selectionSet = []
        self.selectionRect = None

    def selectionStart(self, pos):
        self.startPos      = pos
        self.selectionRect = QRectF(pos, pos + QPointF(1,1))

    def selectionResize(self, p):
        if (r := self.normalizeRect(p, self.startPos)) is None:
             r = QRectF(p, QSize(1, 1))
        self.selectionRect = r

    def selectionEnd(self):
        # select all objects inside the selection rectangle
        for block in self.content.blocks:
            if     prefs.edit.select.enclose and self.selectionRect.contains(block.rect) \
            or not prefs.edit.select.enclose and self.selectionRect.intersects(block.rect):
                self.selectionSet.append(block)
        self.selectionRect = None

    def selectionAdd(self, object):
        if not object in self.selectionSet:
            self.selectionSet.append(object)

    def selectionTranslate(self, delta):
        for s in self.selectionSet:
            s.translate(delta)

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
        self.content.append(Block(
            pos,
            QSizeF(10, 10),
            [ ("reference", "ref?"), ("value", "val?") ]
        ))
        self.content[-1].state |= ItemState.HIGHLIGHTED

    def newBlockResize(self, p):
        n = self.content[-1] # last block in list = new block
        s = self.startPos
        if (r := self.normalizeRect(p, self.startPos)) is None:
            r = QRectF(s, QSizeF(10,10))
        n.setRect(r)

    def newBlockFinish(self):
        self.content[-1].state &= ItemState.HIGHLIGHTED

    def newBlockCancel(self):
        self.content.blocks.pop()

    # return diagram object that was clicked on, or None
    def click(self, pos):
        for item in self.content:
            if QRectF(item.boundingRect).contains(pos):
                return block
        return None

    def draw(self, painter, visibleRect):
        # draw border
        if prefs.dwg.border.enable:
            pen = QPen(prefs.dwg.border.line.color, prefs.dwg.border.line.width, Qt.PenStyle.SolidLine)
            brush = QBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(pen)
            painter.setBrush(brush)
            painter.drawRect(QRect(QPoint(0,0), self.extents-QSize(1,1)))
        # draw contents
        for item in self.content:
            item.draw(painter)
        # draw work in progress - block or selection outline being drawn, etc
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
