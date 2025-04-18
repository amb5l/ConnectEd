from dataclasses import dataclass
from enum        import Enum
from typing      import Optional, Union
from collections import namedtuple
from types       import SimpleNamespace

from PyQt6.QtCore    import Qt, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtGui     import QPen, QBrush, QColor, QFont
from PyQt6.QtWidgets import QGraphicsItem

from ...core import logger, val2str, str2val

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

    def toXml(self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement(self.__class__.__name__)
        for attr_name, attr_type in self.XML_ATTRIBUTES.items():
            if hasattr(self, attr_name):
                xw.writeAttribute(attr_name, val2str(getattr(self, attr_name)))
        for prop_name, (_, _, getter) in self.XML_PROPERTIES.items():
            xw.writeAttribute(prop_name, val2str(getter(self)))
        xw.writeEndElement()

    @classmethod
    def fromXml(cls, xr: QXmlStreamReader) -> 'Element':
        instance = cls()
        attributes = xr.attributes()
        for attribute in attributes:
            if attribute.name() in cls.XML_ATTRIBUTES:
                type_name = cls.XML_ATTRIBUTES[attribute.name()]
                setattr(
                    instance, attribute.name(),
                    str2val(attribute.value(), type_name)
                )
            elif attribute.name() in cls.XML_PROPERTIES:
                type_name, setter, _ = cls.XML_PROPERTIES[attribute.name()]
                setter(instance, str2val(attribute.value(), type_name))

            else:
                logger.warning(f"Unexpected attribute: {attribute.name()}")
        xr.readNext()
        return instance


__all__ = []

from .grip import Grip
__all__ += ['Grip']
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
