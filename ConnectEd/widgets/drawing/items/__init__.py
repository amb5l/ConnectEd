from dataclasses import dataclass
from enum        import Enum
from typing      import Self, Optional, Any
from types       import SimpleNamespace

from PyQt6.QtCore    import Qt, QXmlStreamWriter, QXmlStreamReader, QPointF
from PyQt6.QtGui     import QPen, QBrush, QColor, QFont, QUndoCommand
from PyQt6.QtWidgets import QGraphicsItem

from ....core import val2str, str2val, camel_to_proper, toXmlAttrs, fromXmlAttrs

from .... import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


class ElementLine:
    _element : "Element"
    _color   : Optional[QColor]      # } specified
    _width   : Optional[float]       # }
    _style   : Optional[Qt.PenStyle] # }
    pen      : QPen

    def __init__(
        self    : Self,
        element : "Element",
        color   : Optional[QColor]      = None,
        width   : Optional[float]       = None,
        style   : Optional[Qt.PenStyle] = None
    ) -> None:
        self._element = element
        self._color  = color
        self._width  = width
        self._style  = style
        self.pen     = QPen()
        self.update()

    def getColor(self : Self) -> QColor:
        return self._color

    def setColor(self  : Self, color : QColor) -> None:
        self._color = color
        self.update()

    def getWidth(self : Self) -> float:
        return self._width

    def setWidth(self  : Self, width : float) -> None:
        self._width = width
        self.update()

    def getStyle(self : Self) -> Qt.PenStyle:
        return self._style

    def setStyle(self  : Self, style : Qt.PenStyle) -> None:
        self._style = style
        self.update()

    def update(self : Self) -> None:
        element_name = self._element.__class__.__name__.lower()
        if self._element.isWIP():
            self.pen.setColor(hub.settings.getTheme("wip/line"))
        elif self._element.isSelected():
            self.pen.setColor(hub.settings.getTheme("selected/line"))
        else:
            self.pen.setColor(
                self._color if self._color is not None else \
                    hub.settings.getTheme(f"{element_name}/line")
            )
        p = hub.settings.get(f"prefs/display/elements/{element_name}/line")
        self.pen.setWidthF(self._width if self._width is not None else p.width)
        self.pen.setStyle(self._style if self._style is not None else p.style)

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement("line")
        xw.writeAttribute("color", val2str(self._color))
        xw.writeAttribute("width", val2str(self._width))
        xw.writeAttribute("style", val2str(self._style))
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        attributes = xr.attributes()
        xr.readNext()
        element_line : ElementLine = cls()
        for attr in attributes:
            match attr.name():
                case "color":
                    element_line.setColor(str2val(attr.value(), QColor))
                case "width":
                    element_line.setWidth(str2val(attr.value(), float))
                case "style":
                    element_line.setStyle(str2val(attr.value(), Qt.PenStyle))
        return element_line

class ElementFill:
    _element : "Element"
    _color   : QColor
    _style   : Qt.BrushStyle
    brush    : QBrush

    def __init__(
        self    : Self,
        element : "Element",
        color   : Optional[QColor]        = None,
        style   : Optional[Qt.BrushStyle] = None
    ) -> None:
        self._element = element
        self._color = color
        self._style = style
        self.brush = QBrush()
        self.update()

    def getColor(self : Self) -> QColor:
        return self._color

    def setColor(self  : Self, color : QColor) -> None:
        self._color = color
        self.update()

    def getStyle(self : Self) -> Qt.BrushStyle:
        return self._style

    def setStyle(self  : Self, style : Qt.BrushStyle) -> None:
        self._style = style
        self.update()

    def update(self : Self) -> None:
        element_name = self._element.__class__.__name__.lower()
        prefs = hub.settings.get(f"prefs/display/elements/{element_name}")
        if self._element.isWIP():
            self.brush.setColor(hub.settings.getTheme("wip/fill"))
        elif self._element.isSelected():
            self.brush.setColor(hub.settings.getTheme("selected/fill"))
        else:
            self.brush.setColor(
                self._color if self._color is not None else \
                    hub.settings.getTheme(f"{element_name}/fill")
            )
        self.brush.setStyle(
            self._style if self._style is not None else prefs.fill
        )

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement("fill")
        xw.writeAttribute("color", val2str(self._color))
        xw.writeAttribute("style", val2str(self._style))
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        attributes = xr.attributes()
        xr.readNext()
        element_fill : ElementFill = cls()
        for attr in attributes:
            match attr.name():
                case "color":
                    element_fill.setColor(str2val(attr.value(), QColor))
                case "style":
                    element_fill.setStyle(str2val(attr.value(), Qt.BrushStyle))
        return element_fill

class ElementText:
    _element   : "Element"
    _color     : QColor
    _family    : str
    _size      : float
    _bold      : bool
    _italic    : bool
    _underline : bool
    pen        : QPen
    font       : QFont

    def __init__(
        self      : Self,
        element   : "Element",
        color     : Optional[QColor] = None,
        family    : Optional[str]    = None,
        size      : Optional[float]  = None,
        bold      : Optional[bool]   = None,
        italic    : Optional[bool]   = None,
        underline : Optional[bool]   = None
    ) -> None:
        self._element   = element
        self._color     = color
        self._family    = family
        self._size      = size
        self._bold      = bold
        self._italic    = italic
        self._underline = underline
        self.pen        = QPen()
        self.font       = QFont()
        self.update()

    def getColor(self : Self) -> QColor:
        return self._color

    def setColor(self  : Self, color : QColor) -> None:
        self._color = color
        self.update()

    def getFamily(self : Self) -> str:
        return self._family

    def setFamily(self  : Self, family : str) -> None:
        self._family = family
        self.update()

    def getSize(self : Self) -> float:
        return self._size

    def setSize(self  : Self, size : float) -> None:
        self._size = size
        self.update()

    def getBold(self : Self) -> bool:
        return self._bold

    def setBold(self  : Self, bold : bool) -> None:
        self._bold = bold
        self.update()

    def getItalic(self : Self) -> bool:
        return self._italic

    def setItalic(self  : Self, italic : bool) -> None:
        self._italic = italic
        self.update()

    def getUnderline(self : Self) -> bool:
        return self._underline

    def setUnderline(self  : Self, underline : bool) -> None:
        self._underline = underline
        self.update()

    def update(self : Self) -> None:
        print("update", self._element.isWIP(), self._element.isSelected())
        element_name = self._element.__class__.__name__.lower()
        if self._element.isWIP():
            self.pen.setColor(hub.settings.getTheme("wip/line"))
        elif self._element.isSelected():
            self.pen.setColor(hub.settings.getTheme("selected/line"))
        else:
            self.pen.setColor(
                self._color if self._color is not None else \
                    hub.settings.getTheme(f"{element_name}/text")
            )
        p = hub.settings.get(f"prefs/display/elements/{element_name}/font")
        self.font.setFamily(
            self._family if self._family is not None else p.family
        )
        self.font.setPointSizeF(
            self._size if self._size is not None else p.size
        )
        self.font.setBold(
            self._bold if self._bold is not None else p.bold
        )
        self.font.setItalic(
            self._italic if self._italic is not None else p.italic
        )
        self.font.setUnderline(
            self._underline if self._underline is not None else p.underline
        )

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        vs = val2str
        xw.writeStartElement("text")
        xw.writeAttribute( "color",     vs(self.pen.color()       , QColor ))
        xw.writeAttribute( "family",    vs(self.font.family()     , str    ))
        xw.writeAttribute( "size",      vs(self.font.pointSizeF() , float  ))
        xw.writeAttribute( "bold",      vs(self.font.bold()       , bool   ))
        xw.writeAttribute( "italic",    vs(self.font.italic()     , bool   ))
        xw.writeAttribute( "underline", vs(self.font.underline()  , bool   ))
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        attributes = xr.attributes()
        xr.readNext()
        element_text : ElementText = cls()
        for attr in attributes:
            match attr.name():
                case "color":
                    element_text.setColor(str2val(attr.value(), QColor))
                case "family":
                    element_text.setFamily(str2val(attr.value(), str))
                case "size":
                    element_text.setSize(str2val(attr.value(), float))
                case "bold":
                    element_text.setBold(str2val(attr.value(), bool))
                case "italic":
                    element_text.setItalic(str2val(attr.value(), bool))
                case "underline":
                    element_text.setUnderline(str2val(attr.value(), bool))
        return element_text

class ElementSettings:
    _element : "Element"
    line     : ElementLine
    fill     : ElementFill
    text     : ElementText

    def __init__(
        self     : Self,
        element  : "Element",
        has_line : bool = False,
        has_fill : bool = False,
        has_text : bool = False
    ) -> None:
        self._element = element
        self.line = ElementLine(element) if has_line else None
        self.fill = ElementFill(element) if has_fill else None
        self.text = ElementText(element) if has_text else None
        self.update()
        hub.settings.change.connect(self.update)

    def update(self : Self) -> None:
        if self.line:
            self.line.update()
        if self.fill:
            self.fill.update()
        if self.text:
            self.text.update()

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement("settings")
        if self.line:
            self.line.toXml(xw)
        if self.fill:
            self.fill.toXml(xw)
        if self.text:
            self.text.toXml(xw)
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        element_settings : ElementSettings = cls()
        while not xr.atEnd():
            if xr.isEndElement() and xr.name() == "settings":
                break
            if xr.isStartElement():
                match xr.name():
                    case "line":
                        element_settings.line = ElementLine.fromXml(xr)
                    case "fill":
                        element_settings.fill = ElementFill.fromXml(xr)
                    case "text":
                        element_settings.text = ElementText.fromXml(xr)
        xr.readNext()
        return element_settings

class KPLoc(Enum):
    TOP_LEFT      = (0.0, 0.0)
    TOP_CENTER    = (0.5, 0.0)
    TOP_RIGHT     = (1.0, 0.0)
    CENTER_LEFT   = (0.0, 0.5)
    CENTER        = (0.5, 0.5)
    CENTER_RIGHT  = (1.0, 0.5)
    BOTTOM_LEFT   = (0.0, 1.0)
    BOTTOM_CENTER = (0.5, 1.0)
    BOTTOM_RIGHT  = (1.0, 1.0)

    @property
    def h(self) -> float:
        return self.value[0]

    @property
    def v(self) -> float:
        return self.value[1]

class Element(QGraphicsItem):
    """Base class for all elements."""
    XML_ATTRS = {
        "pos" : (
            "QPointF",
            lambda self, value: self.setPos(value),
            lambda self: self.pos()
        )
    }

    settings : ElementSettings
    wip      : bool

    def __init__(
        self     : Self,
        has_line : bool = False,
        has_fill : bool = False,
        has_text : bool = False,
        wip      : bool = False
    ) -> None:
        # TODO change to has_line, has_fill, has_text
        self.wip = wip
        self.settings = ElementSettings(self, has_line, has_fill, has_text)
        self.setZValue(self.Z)
        f = QGraphicsItem.GraphicsItemFlag
        self.setFlag( f.ItemSendsGeometryChanges      , True  )
        self.setFlag( f.ItemSendsScenePositionChanges , True  )
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)

    def itemChange(
        self   : Self,
        change : QGraphicsItem.GraphicsItemChange,
        value  : Any
    ) -> None:
        if change == self.GraphicsItemChange.ItemSelectedHasChanged:
            self.settings.update()
        return QGraphicsItem.itemChange(self,change, value)

    def setWIP(self : Self, wip : bool) -> None:
        if self.wip != wip:
            self.wip = wip
            self.settings.update()
            self.update()

    def isWIP(self : Self) -> bool:
        return self.wip

    def getPrefs(self : Self) -> SimpleNamespace:
        element_name = self.__class__.__name__.lower()
        return hub.settings.get(f"prefs/display/elements/{element_name}")

    def getTheme(self : Self) -> SimpleNamespace:
        element_name = self.__class__.__name__.lower()
        if self.isSelected():
            theme = hub.settings.getTheme("selected")
        elif self.isWIP():
            theme = hub.settings.getTheme("wip")
        else:
            theme = hub.settings.getTheme(element_name)
        return theme

    def getPrefsTheme(self : Self) -> tuple[SimpleNamespace, SimpleNamespace]:
        element_name = self.__class__.__name__.lower()
        prefs = hub.settings.get(f"prefs/display/elements/{element_name}")
        if self.isSelected():
            theme = hub.settings.getTheme("selected")
        elif self.isWIP():
            theme = hub.settings.getTheme("wip")
        else:
            theme = hub.settings.getTheme(element_name)
        return prefs, theme

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement(self.__class__.__name__)
        self.settings.toXml(xw)
        toXmlAttrs(self, xw)
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr: QXmlStreamReader) -> Self:
        instance = cls()
        instance.settings = ElementSettings.fromXml(xr)
        fromXmlAttrs(instance, xr)
        return instance

class ElementWithGrips(Element):
    """Base class for all elements with grips."""

    grips : dict[KPLoc, "Grip"]

    def __init__(
        self     : Self,
        has_line : bool = False,
        has_fill : bool = False,
        has_text : bool = False,
        wip      : bool = False
    ) -> None:
        super().__init__(has_line, has_fill, has_text, wip)
        self.grips = {kp: self.GRIP_TYPE(self, kp) for kp in self.GRIP_POINTS}
        for grip in self.grips.values():
            grip.setZValue(self.zValue() + grip.Z_DELTA)

    def getKeyPointPos(self : Self, kp : KPLoc) -> QPointF:
        rect = self.gripsRect()
        return QPointF(kp.h * rect.width(), kp.v * rect.height())

    def updateGripsPosition(self : Self) -> None:
        for kp in self.grips.keys():
            p = self.getKeyPointPos(kp)
            self.grips[kp].setPos(p.x(), p.y())

class ElementWithAnchor(ElementWithGrips):
    """Base class for all elements with an anchor."""
    XML_ATTRS = ElementWithGrips.XML_ATTRS | {
        "anchor" : "KPLoc"
    }

    anchor : KPLoc

    def __init__(
        self       : Self,
        anchor     : KPLoc = KPLoc.TOP_LEFT,
        has_line   : bool = False,
        has_fill   : bool = False,
        has_text   : bool = False,
        wip        : bool = False
    ) -> None:
        super().__init__(has_line, has_fill, has_text, wip)
        self.anchor = anchor

    def setAnchor(
        self   : Self,
        anchor : KPLoc = KPLoc.TOP_LEFT
    ) -> None:
        self.anchor = anchor

    def getAnchorOffset(self : Self) -> QPointF:
        return self.getKeyPointPos(self.anchor)

    def setPos(self, pos: QPointF) -> None:
        super().setPos(pos - self.getAnchorOffset())

class cmdElement(QUndoCommand):
    """Base class for all commands that work with an element."""
    scene   : "DrawingScene"
    element : Element

    def __init__(
        self    : Self,
        scene   : "DrawingScene",
        element : Element
    ):
        text = camel_to_proper(self.__class__.__name__.replace("cmd", ""))
        super().__init__(text)
        self.scene = scene
        self.element = element

    def id(self : Self) -> int:
        """Return a unique ID for merging commands."""
        element_id = id(self.element) & 0x7FFFFFFF
        class_id = hash(self.__class__.__name__) & 0x7FFFFFFF
        return ((element_id + class_id) & 0x7FFFFFFF)

    def mergeWith(self : Self, other : QUndoCommand) -> bool:
        """Merge this command with another identical command."""
        if not isinstance(other, self.__class__) \
        or other.scene != self.scene \
        or other.element != self.element:
            return False
        return True

    def redo(self : Self) -> None:
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement redo"
        )

    def undo(self : Self) -> None:
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement undo"
        )

class cmdElements(cmdElement):
    """Base class for all commands that work with multiple elements."""
    elements : list[Element]

    def __init__(
        self     : Self,
        scene    : "DrawingScene",
        elements : list[Element]
    ):
        text = camel_to_proper(self.__class__.__name__.replace("cmd", ""))
        QUndoCommand.__init__(self, text)
        self.scene = scene
        self.elements = elements

    def id(self : Self) -> int:
        """Return a unique ID for merging commands."""
        element_ids = [id(element) & 0x7FFFFFFF for element in self.elements]
        class_id = hash(self.__class__.__name__) & 0x7FFFFFFF
        return ((sum(element_ids) + class_id) & 0x7FFFFFFF)

    def mergeWith(self : Self, other : QUndoCommand) -> bool:
        """Merge this command with another identical command."""
        if not isinstance(other, self.__class__) \
        or other.scene != self.scene \
        or other.elements != self.elements:
            return False
        return True

class cmdPlaceElement(cmdElement):
    """Base class for all commands that place an element."""
    wip      : bool
    has_line : bool
    has_fill : bool
    has_text : bool

    def __init__(
        self       : Self,
        scene      : "DrawingScene",
        element    : Element,
        wip        : bool = False
    ):
        super().__init__(scene, element)
        self.wip = wip

    def id(self : Self) -> int:
            """Return a unique ID for merging commands."""
            element_id = id(self.element) & 0x7FFFFFFF
            class_id = hash(self.__class__.__name__) & 0x7FFFFFFF
            return ((element_id + class_id) & 0x7FFFFFFF)

    def mergeWith(self : Self, other : QUndoCommand) -> bool:
        if not super().mergeWith(other):
            return False
        self.wip = other.wip
        return True

    def redo(self : Self) -> None:
        """Add or update the element in the scene."""
        self.element.setWIP(self.wip)
        self.element.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, not self.wip
        )
        if self.element.scene() != self.scene:
            self.scene.addItem(self.element)

    def undo(self : Self) -> None:
        """Remove the element from the scene."""
        self.scene.removeItem(self.element)

class cmdMove(cmdElements):
    delta : QPointF
    slide : bool

    def __init__(
        self     : Self,
        scene    : "DrawingScene",
        elements : list[Element],
        delta    : QPointF,
        slide    : bool = False
    ):
        super().__init__(scene, elements)
        self.delta = delta
        self.slide = slide

    def mergeWith(self : Self, other : QUndoCommand) -> bool:
        if not super().mergeWith(other):
            return False
        self.delta += other.delta
        return True

    def redo(self : Self) -> None:
        for element in self.elements:
            element.moveBy(self.delta.x(), self.delta.y())
            # TODO: add slide logic

    def undo(self : Self) -> None:
        for element in self.elements:
            element.moveBy(-self.delta.x(), -self.delta.y())
            # TODO: add slide logic

class cmdSlide(cmdMove):
    pass

__all__ = [
    "KPLoc",
    "Element",
    "ElementWithGrips",
    "ElementWithAnchor",
]
from .grip import Grip, ResizeGrip, AnchorGrip
__all__ += grip.__all__
from .rectangle import Rectangle, cmdPlaceRectangle
__all__ += rectangle.__all__
from .text import Text, cmdPlaceText
__all__ += text.__all__
from .symbol_instance import SymbolInstance
__all__ += symbol_instance.__all__
from .block import Block
__all__ += block.__all__

element_class_dict = {}
for class_name in __all__:
    element_class_dict[class_name] = globals()[class_name]
__all__ += ["element_class_dict"]
