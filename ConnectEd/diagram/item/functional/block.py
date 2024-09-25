from PyQt6.QtCore import Qt, QRectF, QPointF, QSizeF, QByteArray, QDataStream
from PyQt6.QtGui import QPen, QBrush
import xml.etree.ElementTree as ET

from common import logger
from prefs import prefs
from diagram_xml import to_xml
from diagram_item import FunctionalItem

class Block(FunctionalItem):
    def __init__(self, rect, properties):
        super().__init__(
            self.Type.BLOCK,
            rect.topLeft(),
            properties
        )

        # block specific
        self.size = rect.size()



    # detect if p hits this block or any of its child objects
    def select(self, p):
        # handle point or rect

        # check child objects
        for _, property in self.properties.items():
            if property.select(p):
                return True
        # check block outline and fill
        w = prefs().draw.block.line.width / 2
        o = QPointF(w, w)
        r = QRectF(self.rect.topLeft()  - o, self.rect.topRight() + o)
        if r.contains(p):
            self.state |= ItemState.SELECTED
        return True



    def setRect(self, rect):
        self.rect = rect

    def setSize(self, size):
        self.rect.setSize(size)

    def setPosition(self, position):
        self.rect.moveTo(position)



    def blockNewStart(self, pos):
        self.startPos = pos
        self.content.append(Block(
            pos,
            QSizeF(10, 10),
            [ ("reference", "ref?"), ("value", "val?") ]
        ))
        self.content[-1].state |= ItemState.HIGHLIGHTED

    def blockNewResize(self, p):
        n = self.content[-1] # last block in list = new block
        s = self.startPos
        if (r := self.normalizeRect(p, self.startPos)) is None:
            r = QRectF(s, QSizeF(10,10))
        n.setRect(r)

    def newBlockFinish(self):
        self.content[-1].state &= self.State.HIGHLIGHTED

    def newBlockCancel(self):
        self.content.blocks.pop()

    #-------------------------------------------------------------------------------
    # selection

    def select(self, x):
        '''
        Returns:
            list: either contains self, or is empty
        '''
        # trivial rejection
        if not self.selectBoundingRect(x):
            return
        # check pins
        if prefs().select.filter.pins:
            for pin in self.pins:
                if pin.select(x):
                    return [self]
        # check properties
        if prefs().select.filter.properties:
        # check self, allowing for line thickness
        w = prefs().draw.block.line.width / 2
        o = QPointF(w, w)
        r = QRectF(self.rect.topLeft()  - o, self.rect.bottomRight() + o)
        if type(x) is QPointF:
            if r.contains(p):
                self.state |= self.State.SELECTED
            return True



            return self.brect.contains(x)
        elif type(x) is QRectF:

        else:
            logger.warning(f"Block.select: unsupported type = {type(x)}")

    #-------------------------------------------------------------------------------
    # paint

    def draw(self, painter, alpha=255):
        pen, brush = self.penBrush(
            self.state,
            prefs().draw.block,
            prefs().theme.block,
            alpha
        )
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRect(self.rect)
        # draw properties
        for _, p in self.properties.items():
            p.draw(painter)

    #-------------------------------------------------------------------------------
    # serialize/deserialize (to/from clipboard, file)

        # serialize to XML for clipboard and file save
    def to_xml(self, writer):
        writer.writeStartElement('block')
        to_xml('rect', self.rect, writer)
        to_xml('properties', self.properties, writer)
        writer.endElement() # block

    # deserialize from XML for clipboard and file load
    def from_xml(self, element):
        for child in element:
            if child.tag == 'rect':
                self.rect = QRectF()
                self.rect.from_xml(child)
            elif child.tag == 'properties':
                self.properties = {}
                for prop in child:
                    p = Property()
                    p.from_xml(prop)
                    self.properties[p.name] = p