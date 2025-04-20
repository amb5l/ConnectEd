from dataclasses import dataclass
from enum        import Enum
from typing      import Self, Optional
from collections import namedtuple
from types       import SimpleNamespace

from PyQt6.QtCore    import Qt, QXmlStreamWriter, QXmlStreamReader, QPointF
from PyQt6.QtGui     import QPen, QBrush, QColor, QFont, QUndoCommand
from PyQt6.QtWidgets import QGraphicsItem

from ...core import logger, val2str, str2val, camel_to_proper

from .grip import Grip

from ... import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene

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

class Element(QGraphicsItem):
    """Base class for all elements."""

    def __init__(
        self       : Self,
        pen_spec   : bool | PenSpec   = False,
        brush_spec : bool | BrushSpec = False,
        text_spec  : bool | TextSpec  = False
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

    def getWIP(self : Self) -> bool:
        return False if self.scene() is None else \
            self in self.scene().wip

    def getPrefsTheme(self : Self) -> SimpleNamespace:
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
        self     : Self,
        pen_spec : PenSpec = PenSpec()
    ) -> None:
        self.pen_spec = pen_spec

    def getPenSpec(self : Self) -> PenSpec:
        return self.pen_spec

    def penFromSpec(self : Self) -> QPen:
        if not hasattr(self, 'pen_spec'):
            return QPen(Qt.PenStyle.NoPen)
        prefs, theme = self.getPrefsTheme()
        s = self.pen_spec
        color = theme.line if s.color is None else s.color
        color.setAlpha(hub.settings.prefs.display.elements.alpha)
        width = prefs.line.width if s.width is None else s.width
        style = prefs.line.style if s.style is None else s.style
        return QPen(color, width, style)

    def penWidth(self : Self) -> float:
        if not hasattr(self, 'pen_spec'):
            return 0
        prefs, _ = self.getPrefsTheme()
        s = self.pen_spec
        return prefs.line.width if s.width is None else s.width

    def setBrushSpec(
        self       : Self,
        brush_spec : BrushSpec = BrushSpec()
    ) -> None:
        self.brush_spec = brush_spec

    def getBrushSpec(self : Self) -> BrushSpec:
        return self.brush_spec

    def brushFromSpec(self : Self) -> QBrush:
        if not hasattr(self, 'brush_spec'):
            return QBrush(Qt.BrushStyle.NoBrush)
        prefs, theme = self.getPrefsTheme()
        s = self.brush_spec
        color = theme.fill if s.color is None else s.color
        color.setAlpha(hub.settings.prefs.display.elements.alpha)
        style = prefs.fill if s.style is None else s.style
        return QBrush(color, style)

    def setTextSpec(
        self      : Self,
        text_spec : TextSpec = TextSpec()
    ) -> None:
        self.text_spec = text_spec

    def getTextSpec(self : Self) -> TextSpec:
        return self.text_spec

    def fontFromSpec(self : Self) -> QFont | None: # TODO: return default font?
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

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement(self.__class__.__name__)
        for attr_name, attr_type in self.XML_ATTRIBUTES.items():
            if hasattr(self, attr_name):
                xw.writeAttribute(attr_name, val2str(getattr(self, attr_name)))
        for prop_name, (_, _, getter) in self.XML_PROPERTIES.items():
            xw.writeAttribute(prop_name, val2str(getter(self)))
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr: QXmlStreamReader) -> Self:
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

class cmdElement(QUndoCommand):
    scene   : 'DrawingScene'
    element : Element

    def __init__(
        self       : Self,
        scene      : 'DrawingScene',
        element    : Optional[Element] = None,
        wip        : bool = False
    ):
        cls_name = self.__class__.__name__
        text = camel_to_proper(cls_name.replace('cmd', ''))
        super().__init__(text)
        self.scene = scene
        if element is None:
            element_class_name = cls_name.replace('cmdPlace', '')
            element = globals()[element_class_name]()
        self.element = element
        self.element.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, not wip
        )

    def mergeWith(self : Self, other : QUndoCommand) -> bool:
        """Merge this command with another identical command."""
        if not isinstance(other, self.__class__) \
        or other.scene != self.scene \
        or other.element != self.element:
            return False
        return True

    def redo(self : Self) -> None:
        raise NotImplementedError(
            f'{self.__class__.__name__} must implement redo'
        )

    def undo(self : Self) -> None:
        raise NotImplementedError(
            f'{self.__class__.__name__} must implement undo'
        )

class cmdPlaceElement(cmdElement):
    wip        : bool
    pen_spec   : bool | PenSpec
    brush_spec : bool | BrushSpec
    text_spec  : bool | TextSpec

    def __init__(
        self       : Self,
        scene      : 'DrawingScene',
        element    : Optional[Element] = None,
        pen_spec   : bool | PenSpec   = True,
        brush_spec : bool | BrushSpec = True,
        text_spec  : bool | TextSpec  = True,
        wip        : bool = False
    ):
        super().__init__(scene, element)
        self.pen_spec   = pen_spec
        self.brush_spec = brush_spec
        self.text_spec  = text_spec
        self.wip        = wip

    def id(self : Self) -> int:
            """Return a unique ID for merging commands."""
            element_id = id(self.element) & 0x7FFFFFFF
            class_id = hash(self.__class__.__name__) & 0x7FFFFFFF
            return ((element_id + class_id) & 0x7FFFFFFF)

    def mergeWith(self : Self, other : QUndoCommand) -> bool:
        if not super().mergeWith(other):
            return False
        self.pen_spec   = other.pen_spec
        self.brush_spec = other.brush_spec
        self.text_spec  = other.text_spec
        self.wip        = other.wip
        return True

    def redo(self : Self) -> None:
        """Add or update the element in the scene."""
        if self.element.scene() != self.scene:
            self.scene.addItem(self.element)
        self.scene.wip = [self.element] if self.wip else []
        self.element.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, not self.wip
        )

    def undo(self : Self) -> None:
        """Remove the element from the scene."""
        self.scene.removeItem(self.element)
        self.scene.wip = []

class cmdMoveGrip(cmdElement):
    delta   : QPointF

    def __init__(
        self       : Self,
        scene      : 'DrawingScene',
        element    : Element,
        delta      : QPointF
    ):
        super().__init__(scene, element)
        self.delta = delta

    def mergeWith(self : Self, other : QUndoCommand) -> bool:
        if not super().mergeWith(other):
            return False
        self.delta = other.delta
        return True

    def redo(self : Self):
        self.element.parentItem().moveKeyPoint(self.element.key_point, self.delta)

    def undo(self : Self):
        self.element.parentItem().moveKeyPoint(self.element.key_point, -self.delta)

__all__ = []

from .grip import Grip
__all__ += ['Grip']
from .rectangle import Rectangle, cmdPlaceRectangle
__all__ += rectangle.__all__
from .symbol_instance import SymbolInstance
__all__ += symbol_instance.__all__
from .block import Block
__all__ += block.__all__

element_class_dict = {}
for class_name in __all__:
    element_class_dict[class_name] = globals()[class_name]
__all__ += ['element_class_dict']
