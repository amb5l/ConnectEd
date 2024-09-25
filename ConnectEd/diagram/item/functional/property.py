from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPen, QBrush, QFont
from enum import Enum

from prefs.prefs import prefs
from diagram_text import TextLine

class ItemPropertyMixin:
    class Property(TextLine):
        class Visibility(Enum):
            NONE  = 0
            VALUE = 1
            BOTH  = 2

        def __init__(
            self,
            parent,
            name,
            value,
            anchor,
            visibility=Visibility.VALUE,
            rotation = 0.0,
        ):
            super().__init__()
            self.parent       = parent       # e.g. block
            self.name         = name
            self.value        = value
            self.anchor       = anchor       # e.g. BlockPropertyAnchor
            self.visibility   = visibility   # bool
            self.rotation     = rotation     # int

            self.boundingRect = None
            self.selected     = False
            self.highlighted  = False

        def selectPoint(self, p):
            if self.boundingRect is None:
                return False
            elif self.boundingRect.contains(p):
                self.selected = True
                return True # signifies hit, no need to consider other objects
            return False

        def selectTogglePoint(self, p):
            if self.boundingRect is None:
                return False
            elif self.boundingRect.contains(p):
                self.selected = not self.selected
                return True # signifies hit, no need to consider other objects
            return False

        def selectRect(self, r):
            if self.boundingRect is None:
                return
            elif prefs().edit.select.enclose and r.contains(self.boundingRect):
                self.selected = True
            elif r.intersects(self.boundingRect):
                self.selected = True
            return

        def deselect(self):
            self.selected = False

        def draw(self, painter, alpha=255):
            match self.visibility:
                case self.Visibility.NONE:
                    return
                case self.Visibility.VALUE:
                    text = self.value
                case self.Visibility.BOTH:
                    text = self.name + "=" + self.value
            painter.save()
            color = prefs().draw.theme.block.property
            color.setAlpha(alpha)
            pen = QPen(color, 0.0, Qt.PenStyle.SolidLine) # TODO investigate effect of line width
            brush = QBrush(color)
            if self.highlighted:
                pen.setColor(prefs().draw.theme.highlighted.line)
                brush.setColor(prefs().draw.theme.highlighted.fill)
            elif self.selected:
                pen.setColor(prefs().draw.theme.selected.line)
                brush.setColor(prefs().draw.theme.selected.fill)
            painter.setPen(pen)
            painter.setBrush(brush)
            font = QFont(
                prefs().draw.block.property.font.family,
                prefs().draw.block.property.font.size,
                prefs().draw.block.property.font.bold,
                prefs().draw.block.property.font.italic
            )
            painter.setFont(font)
            flags = Qt.TextFlag.TextSingleLine
            if self.boundingRect == None:
                self.boundingRect = painter.boundingRect(QRectF(0,0,1,1), flags, text)
            position = self.getRectAnchorPoint(self.parent.rect, self.anchor.remote) + \
                    self.anchor.offset - \
                    self.getRectAnchorOffset(self.boundingRect, self.anchor.local)
            painter.rotate(-self.rotation)
            painter.translate(position)
            painter.drawText(self.boundingRect, flags, text)
            if prefs().draw.block.property.outline:
                pen = QPen(color, 0, Qt.PenStyle.SolidLine)
                brush = QBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(pen)
                painter.setBrush(brush)
                painter.drawRect(self.boundingRect)
            painter.restore()
