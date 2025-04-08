from dataclasses import dataclass
from enum        import Enum
from typing      import Optional, Union
from collections import namedtuple
from types       import SimpleNamespace

from PyQt6.QtCore    import Qt, QPointF, QRectF, QSizeF, \
                            QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtGui     import QPainter, QPen, QBrush, QColor, QFont, QPainterPath
from PyQt6.QtWidgets import QStyleOptionGraphicsItem, QWidget, \
                            QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem

from ...core import val2str, str2val

from .grip import Grip

from ... import hub


@dataclass
class PenSpec:
    color : Optional[QColor]      = None
    width : Optional[float]       = None
    style : Optional[Qt.PenStyle] = None

@dataclass
class BrushSpec:
    color : Optional[QColor]        = None
    style : Optional[Qt.BrushStyle] = None

@dataclass
class TextSpec:
    color     : Optional[QColor] = None
    family    : Optional[str]    = None
    size      : Optional[float]  = None # TODO: 0 = resize with parent boundary?
    weight    : Optional[int]    = None
    italic    : Optional[bool]   = None
    underline : Optional[bool]   = None

KeyPointHV = namedtuple('KeyPointHV', ['h', 'v'])

class KeyPoint(Enum):
    TOP_LEFT      = KeyPointHV(0.0, 0.0)
    TOP_CENTER    = KeyPointHV(0.5, 0.0)
    TOP_RIGHT     = KeyPointHV(1.0, 0.0)
    CENTER_LEFT   = KeyPointHV(0.0, 0.5)
    CENTER        = KeyPointHV(0.5, 0.5)
    CENTER_RIGHT  = KeyPointHV(1.0, 0.5)
    BOTTOM_LEFT   = KeyPointHV(0.0, 1.0)
    BOTTOM_CENTER = KeyPointHV(0.5, 1.0)
    BOTTOM_RIGHT  = KeyPointHV(1.0, 1.0)

class Element:
    """Base class for all elements."""
    def __init__(
        self,
        pen_spec   : Union[ bool, PenSpec   ] = False,
        brush_spec : Union[ bool, BrushSpec ] = False,
        text_spec  : Union[ bool, TextSpec  ] = False
    ) -> None:
        if pen_spec:
            self.pen_spec = PenSpec(None, None, None) \
                if pen_spec is True else pen_spec
        if brush_spec:
            self.brush_spec = BrushSpec(None, None) \
                if brush_spec is True else brush_spec
        if text_spec:
            self.text_spec = TextSpec(None, None, None, None, None, None) \
                if text_spec is True else text_spec
        f = QGraphicsItem.GraphicsItemFlag
        self.setFlag( f.ItemSendsGeometryChanges             , True  )
        self.setFlag( f.ItemSendsScenePositionChanges        , True  )
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)

    def getWIP(self) -> bool:
        return False if self.scene() is None else \
            self in self.scene().wip

    def getPrefsTheme(self) -> SimpleNamespace:
        element_name = self.__class__.__name__.lower()
        if self.isSelected():
            prefs = hub.settings.prefs.display.elements.selected
            theme = hub.settings.theme.selected
        elif self.getWIP():
            prefs = hub.settings.prefs.display.elements.wip
            theme = hub.settings.theme.wip
        else:
            prefs = getattr(hub.settings.prefs.display.elements, element_name)
            theme = getattr(hub.settings.theme, element_name)
        return prefs, theme

    def setPenSpec(
        self,
        pen_spec : PenSpec = PenSpec()
    ) -> None:
        self.pen_spec = pen_spec

    def getPenSpec(self) -> PenSpec:
        return self.pen_spec

    def penFromSpec(self) -> QPen:
        if not hasattr(self, 'pen_spec'):
            return QPen(Qt.PenStyle.NoPen)
        prefs, theme = self.getPrefsTheme()
        s = self.pen_spec
        color = theme.line if s.color is None else s.color
        color.setAlpha(hub.settings.prefs.display.elements.alpha)
        width = prefs.line.width if s.width is None else s.width
        style = prefs.line.style if s.style is None else s.style
        return QPen(color, width, style)

    def penWidth(self) -> float:
        if not hasattr(self, 'pen_spec'):
            return 0
        prefs, _ = self.getPrefsTheme()
        s = self.pen_spec
        return prefs.line.width if s.width is None else s.width

    def setBrushSpec(
        self,
        brush_spec : BrushSpec = BrushSpec()
    ) -> None:
        self.brush_spec = brush_spec

    def getBrushSpec(self) -> BrushSpec:
        return self.brush_spec

    def brushFromSpec(self) -> QBrush:
        if not hasattr(self, 'brush_spec'):
            return QBrush(Qt.BrushStyle.NoBrush)
        prefs, theme = self.getPrefsTheme()
        s = self.brush_spec
        color = theme.fill if s.color is None else s.color
        color.setAlpha(hub.settings.prefs.display.elements.alpha)
        style = prefs.fill if s.style is None else s.style
        return QBrush(color, style)

    def setTextSpec(
        self,
        text_spec : TextSpec = TextSpec()
    ) -> None:
        self.text_spec = text_spec

    def getTextSpec(self) -> TextSpec:
        return self.text_spec

    def fontFromSpec(self) -> QFont | None: # TODO: return default font?
        if not hasattr(self, 'text_spec'):
            return None
        item_name = self.__class__.__name__.lower()
        prefs = getattr(hub.settings.prefs.display.elements, item_name).font
        theme = getattr(hub.settings.theme, item_name).font
        self.setDefaultTextColor(
            theme.color if self.text_spec.color is None else
                self.text_spec.color
        )
        self.font.setFamily(
            prefs.family if self.text_spec.family is None else
                self.text_spec.family
        )
        self.font.setPointSizeF(
            prefs.size if self.text_spec.size is None else
                self.text_spec.size
        )
        self.font.setWeight(
            prefs.weight if self.text_spec.weight is None else
                self.text_spec.weight
        )
        self.font.setItalic(
            prefs.italic if self.text_spec.italic is None else
                self.text_spec.italic
        )

class ElementXmlMixin:
    def toXml(self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement(self.__class__.__name__)
        for attr_name, attr_type in self.XML_ATTRIBUTES.items():
            if hasattr(self, attr_name):
                xw.writeAttribute(attr_name, val2str(getattr(self, attr_name)))
        for prop_name, type_setter_getter in self.XML_PROPERTIES.items():
            _, _, getter = type_setter_getter
            xw.writeAttribute(prop_name, val2str(getter(self)))
        xw.writeEndElement()

    @classmethod
    def fromXml(cls, xr: QXmlStreamReader) -> 'RectElement':
        instance = cls()
        for prop_name, attr_type_name in instance.XML_ATTRIBUTES.items():
            if hasattr(instance, prop_name):
                setattr(
                    instance, prop_name,
                    str2val(xr.attributes().value(prop_name), attr_type_name)
                )
        for prop_name, type_setter_getter in cls.XML_PROPERTIES.items():
            prop_type_name, setter, _ = type_setter_getter  # Unpack just 2 items
            if xr.attributes().hasAttribute(prop_name):
                setter(instance, str2val(xr.attributes().value(prop_name), prop_type_name))
            else:
                raise ValueError(f'Unexpected attribute: {prop_name}')
        xr.readNext()
        return instance

class RectElement(QGraphicsRectItem, Element, ElementXmlMixin):
    """Base class for rectangle items."""
    XML_ATTRIBUTES = {
        'anchor'     : 'KeyPoint',
        'pen_spec'   : 'PenSpec',
        'brush_spec' : 'BrushSpec',
        'text_spec'  : 'TextSpec'
    }
    XML_PROPERTIES = {
        'pos'  : ( 'QPointF' , lambda self, value: self.setPos(value)  , lambda self: self.pos()         ),
        'size' : ( 'QSizeF'  ,  lambda self, value: self.setSize(value) , lambda self: self.rect().size() )
    }
    MIN_SIZE = QSizeF(1.0, 1.0)

    anchor : KeyPoint
    grips  : dict[KeyPoint, Grip]

    def __init__(
        self,
        pos        : QPointF = QPointF(0, 0),
        size       : QSizeF = QSizeF(0, 0),
        anchor     : KeyPoint = KeyPoint.TOP_LEFT,
        pen_spec   : Union[ bool, PenSpec   ] = True,
        brush_spec : Union[ bool, BrushSpec ] = True,
        text_spec  : Union[ bool, TextSpec  ] = False
    ) -> None:
        QGraphicsRectItem.__init__(self)
        Element.__init__(self, pen_spec, brush_spec, text_spec)
        self.grips = {p: Grip(self, p) for p in KeyPoint if p != KeyPoint.CENTER}
        self.anchor = anchor
        self.setPosSize(pos, size)
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        self.setZValue(self.Z)
        self.setAnchor(anchor)
        self.updateGripsPosition()
        self.updateGripsVisibility()
        self.updateGripsZValue()

    def setSize(self, size : QSizeF) -> None:
        self.setRect(0, 0, size.width(), size.height())

    def getSize(self) -> QSizeF:
        return self.rect().size()

    def setAnchor(self, anchor : KeyPoint = KeyPoint.TOP_LEFT) -> None:
        self.anchor = anchor

    def getAnchor(self) -> KeyPoint:
        return self.anchor

    def setPosSize(self, pos : QPointF, size : QSizeF) -> None:
        self.setPos(pos)
        if size.width() < self.MIN_SIZE.width():
            size.setWidth(self.MIN_SIZE.width())
        if size.height() < self.MIN_SIZE.height():
            size.setHeight(self.MIN_SIZE.height())
        self.setRect(0, 0, size.width(), size.height())
        self.updateGripsPosition()

    def setPoints(self, p1_or_x1, p2_or_y1=None, x2=None, y2=None) -> None:
        if p2_or_y1 is not None and x2 is not None and y2 is not None:
            p1, p2 = QPointF(p1_or_x1, p2_or_y1), QPointF(x2, y2)
        else:
            p1, p2 = p1_or_x1, p2_or_y1
        rect = QRectF(p1, p2).normalized()
        self.setPosSize(rect.topLeft(), rect.size())

    def getPoints(self) -> tuple[QPointF, QPointF]:
        return self.pos(), self.pos() + self.rect().bottomRight()

    def updateGripsPosition(self) -> None:
        for kp in self.grips.keys():
            self.grips[kp].setPos(
                kp.value.h * self.rect().width(),
                kp.value.v * self.rect().height()
            )

    def updateGripsVisibility(self) -> None:
        for grip in self.grips.values():
            grip.setVisible(
                self.isSelected() and len(self.scene().selectedItems()) == 1
            )

    def updateGripsZValue(self) -> None:
        for grip in self.grips.values():
            grip.setZValue(self.zValue() + Grip.Z_DELTA)

    def gripResize(self, kp : KeyPoint, delta : QPointF) -> None:
        p1, p2 = self.getPoints()
        d = delta
        match kp:
            case KeyPoint.TOP_LEFT:
                self.setPoints(p1 + d, p2)
            case KeyPoint.TOP_CENTER:
                self.setPoints(p1.x(), p1.y() + d.y(), p2.x(), p2.y())
            case KeyPoint.TOP_RIGHT:
                self.setPoints(p1.x(), p1.y() + d.y(), p2.x() + d.x(), p2.y())
            case KeyPoint.CENTER_LEFT:
                self.setPoints(p1.x() + d.x(), p1.y(), p2.x(), p2.y())
            case KeyPoint.CENTER_RIGHT:
                self.setPoints(p1.x(), p1.y(), p2.x() + d.x(), p2.y())
            case KeyPoint.BOTTOM_LEFT:
                self.setPoints(p1.x() + d.x(), p1.y(), p2.x(), p2.y() + d.y())
            case KeyPoint.BOTTOM_CENTER:
                self.setPoints(p1.x(), p1.y() + d.y(), p2.x(), p2.y())
            case KeyPoint.BOTTOM_RIGHT:
                self.setPoints(p1, p2 + d)
            case _:
                raise ValueError(f'Invalid key point: {kp}')

    def rect(self) -> QRectF:
        rect = super().rect()
        rect.translate(
            -self.anchor.value.h * rect.width(),
            -self.anchor.value.v * rect.height()
        )
        return rect

    def boundingRect(self) -> QRectF:
        w = max(
            self.penWidth(),
            hub.settings.prefs.display.elements.selected.grip.size
        )
        return self.rect().adjusted(-w/2, -w/2, w/2, w/2)

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def paint(
        self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        pen = self.penFromSpec()
        painter.setPen(pen)
        brush = self.brushFromSpec()
        painter.setBrush(brush)
        painter.drawRect(QRectF(
            -self.rect().width() * self.anchor.value.h,
            -self.rect().height() * self.anchor.value.v,
            self.rect().width(),
            self.rect().height()
        ))

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.updateGripsVisibility()
        return super().itemChange(change, value)

class TextItem(QGraphicsTextItem, Element, ElementXmlMixin):
    """Base class for text items."""
    XML_ATTRIBUTES = {
        'text'       : ( 'str'       , lambda self, value: self.setText      (value) , lambda self: self.getText      () ),
        'pos'        : ( 'QPointF'   , lambda self, value: self.setPos       (value) , lambda self: self.getPos       () ),
        'anchor'     : ( 'KeyPoint'  , lambda self, value: self.setAnchor    (value) , lambda self: self.getAnchor    () ),
        'pen_spec'   : ( 'PenSpec'   , lambda self, value: self.setPenSpec   (value) , lambda self: self.getPenSpec   () ),
        'brush_spec' : ( 'BrushSpec' , lambda self, value: self.setBrushSpec (value) , lambda self: self.getBrushSpec () ),
        'text_spec'  : ( 'TextSpec'  , lambda self, value: self.setTextSpec  (value) , lambda self: self.getTextSpec  () )
    }

    anchor : KeyPoint

    def __init__(
        self,
        text       : str = '',
        pos        : QPointF = QPointF(0, 0),
        anchor     : KeyPoint = KeyPoint.TOP_LEFT,
        pen_spec   : Union[ bool, PenSpec   ] = False,
        brush_spec : Union[ bool, BrushSpec ] = False,
        text_spec  : Union[ bool, TextSpec  ] = True
    ) -> None:
        QGraphicsTextItem.__init__(self, text)
        Element.__init__(self, pen_spec, brush_spec, text_spec)
        self.setPos(pos)
        self.setZValue(self.Z)
        self.setAnchor(anchor)
        self.setTextSpec()

    def setAnchor(self, anchor : KeyPoint = KeyPoint.TOP_LEFT) -> None:
        self.anchor = anchor

    def boundingRect(self) -> QRectF:
        rect = super().boundingRect()
        return QRectF(
            -rect.width() * self.anchor.value.h,
            -rect.height() * self.anchor.value.v,
            rect.width(), rect.height()
        )

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def paint(
        self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        self.fontFromSpec()
        self.setFont(self.font)
        rect = self.anchoredBoundingRect()
        painter.translate(rect.topLeft())
        painter.drawText(
            rect,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
            self.toPlainText()
        )

__all__ = []

from .rectangle import Rectangle
__all__ += rectangle.__all__
from .symbol_instance import SymbolInstance
__all__ += symbol_instance.__all__
from .block import Block
__all__ += block.__all__

element_class_dict = {}
for class_name in __all__:
    element_class_dict[class_name] = globals()[class_name]
__all__ += ['element_class_dict']
