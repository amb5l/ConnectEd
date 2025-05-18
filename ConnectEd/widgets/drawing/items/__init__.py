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
    from .. import Drawing


class LinePen:
    _element : "Element"
    _display : str
    _theme   : str
    _color   : Optional[QColor]
    _width   : Optional[float]
    _style   : Optional[Qt.PenStyle]
    normal   : QPen
    selected : QPen
    pen      : QPen

    def __init__(self : Self, element : "Element") -> None:
        self._element = element
        self._color   = None
        self._width   = None
        self._style   = None
        self.normal   = QPen()
        self.selected = QPen()
        self.onSettingsChange()

    def getColor(self : Self) -> QColor:
        return self._color

    def setColor(self  : Self, color : QColor) -> None:
        self._color = color
        self.onSettingsChange()

    def getWidth(self : Self) -> float:
        return self._width

    def setWidth(self  : Self, width : float) -> None:
        self._width = width
        self.onSettingsChange()

    def getStyle(self : Self) -> Qt.PenStyle:
        return self._style

    def setStyle(self  : Self, style : Qt.PenStyle) -> None:
        self._style = style
        self.onSettingsChange()

    def getDefaults(self : Self) -> SimpleNamespace:
        element_name = self._element.__class__.__name__
        r = hub.settings.get(f"defaults/elements/{element_name}/line")
        r.color = hub.settings.getTheme(f"elements/{element_name}/line")
        return r

    def onSettingsChange(self : Self) -> None:
        default = self.getDefaults()
        color_normal = default.color if self._color is None else self._color
        color_selected = hub.settings.getTheme("selected/line")
        width = default.width if self._width is None else self._width
        style = default.style if self._style is None else self._style
        self.normal.setColor(color_normal)
        self.normal.setWidthF(width)
        self.normal.setStyle(style)
        self.selected.setColor(color_selected)
        self.selected.setWidthF(width)
        self.selected.setStyle(style)
        self.onSelectionChange()

    def onSelectionChange(self : Self) -> None:
        self.pen = self.selected if self._element.isSelected() else self.normal

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
        element_line : LinePen = cls()
        for attr in attributes:
            match attr.name():
                case "color":
                    element_line.setColor(str2val(attr.value(), QColor))
                case "width":
                    element_line.setWidth(str2val(attr.value(), float))
                case "style":
                    element_line.setStyle(str2val(attr.value(), Qt.PenStyle))
        return element_line

class FillBrush:
    _element : "Element"
    _color   : QColor
    _style   : Qt.BrushStyle
    normal   : QBrush
    selected : QBrush
    brush    : QBrush

    def __init__(
        self    : Self,
        element : "Element",
        color   : Optional[QColor]        = None,
        style   : Optional[Qt.BrushStyle] = None
    ) -> None:
        self._element = element
        self._color   = color
        self._style   = style
        self.normal   = QBrush()
        self.selected = QBrush()
        self.onSettingsChange()

    def getColor(self : Self) -> QColor:
        return self._color

    def setColor(self  : Self, color : QColor) -> None:
        self._color = color
        self.onSettingsChange()

    def getStyle(self : Self) -> Qt.BrushStyle:
        return self._style

    def setStyle(self  : Self, style : Qt.BrushStyle) -> None:
        self._style = style
        self.onSettingsChange()

    def getDefaults(self : Self) -> SimpleNamespace:
        r = SimpleNamespace()
        element_name = self._element.__class__.__name__
        r.style = hub.settings.get(f"defaults/elements/{element_name}/fill")
        r.color = hub.settings.getTheme(f"elements/{element_name}/fill")
        return r

    def onSettingsChange(self : Self) -> None:
        default = self.getDefaults()
        color_normal = default.color if self._color is None else self._color
        color_selected = hub.settings.getTheme("selected/fill")
        style = default.style if self._style is None else self._style
        self.normal.setColor(color_normal)
        self.normal.setStyle(style)
        self.selected.setColor(color_selected)
        self.selected.setStyle(style)
        self.onSelectionChange()

    def onSelectionChange(self : Self) -> None:
        self.brush = self.selected if self._element.isSelected() else self.normal

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement("fill")
        xw.writeAttribute("color", val2str(self._color))
        xw.writeAttribute("style", val2str(self._style))
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        attributes = xr.attributes()
        xr.readNext()
        element_fill : FillBrush = cls()
        for attr in attributes:
            match attr.name():
                case "color":
                    element_fill.setColor(str2val(attr.value(), QColor))
                case "style":
                    element_fill.setStyle(str2val(attr.value(), Qt.BrushStyle))
        return element_fill

class TextColorFont:
    _element   : "Element"
    _color     : Optional[QColor]
    _family    : Optional[str]
    _size      : Optional[float]
    _bold      : Optional[bool]
    _italic    : Optional[bool]
    _underline : Optional[bool]
    normal     : QColor
    selected   : QColor
    color      : QColor
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
        self.normal     = QColor()
        self.selected   = QColor()
        self.font       = QFont()
        self.onSettingsChange()

    def set(
        self      : Self,
        color     : Optional[QColor] = None,
        family    : Optional[str]    = None,
        size      : Optional[float]  = None,
        bold      : Optional[bool]   = None,
        italic    : Optional[bool]   = None,
        underline : Optional[bool]   = None
    ) -> None:
        if color:     self._color     = color
        if family:    self._family    = family
        if size:      self._size      = size
        if bold:      self._bold      = bold
        if italic:    self._italic    = italic
        if underline: self._underline = underline
        self.onSettingsChange()

    def getColor(self : Self) -> Optional[QColor]:
        return self._color

    def setColor(self  : Self, color : Optional[QColor]) -> None:
        self._color = color
        self.onSettingsChange()

    def getFamily(self : Self) -> Optional[str]:
        return self._family

    def setFamily(self  : Self, family : Optional[str]) -> None:
        self._family = family
        self.onSettingsChange()

    def getSize(self : Self) -> Optional[float]:
        return self._size

    def setSize(self  : Self, size : Optional[float]) -> None:
        self._size = size
        self.onSettingsChange()

    def getBold(self : Self) -> Optional[bool]:
        return self._bold

    def setBold(self  : Self, bold : Optional[bool]) -> None:
        self._bold = bold
        self.onSettingsChange()

    def getItalic(self : Self) -> Optional[bool]:
        return self._italic

    def setItalic(self  : Self, italic : Optional[bool]) -> None:
        self._italic = italic
        self.onSettingsChange()

    def getUnderline(self : Self) -> Optional[bool]:
        return self._underline

    def setUnderline(self  : Self, underline : Optional[bool]) -> None:
        self._underline = underline
        self.onSettingsChange()

    def getDefaults(self : Self) -> SimpleNamespace:
        element_name = self._element.__class__.__name__
        r = hub.settings.get(f"defaults/elements/{element_name}/text")
        r.color = hub.settings.getTheme(f"elements/{element_name}/text")
        return r

    def onSettingsChange(self : Self) -> None:
        element_name = self._element.__class__.__name__
        self.selected.setRgb(hub.settings.getTheme("selected/text").rgb())
        default = self.getDefaults()
        self.normal.setRgb(
            default.color.rgb() if self._color is None else self._color.rgb()
        )
        self.font.setFamily(
            default.family if self._family is None else self._family
        )
        self.font.setPointSizeF(
            default.size if self._size is None else self._size
        )
        self.font.setBold(
            default.bold if self._bold is None else self._bold
        )
        self.font.setItalic(
            default.italic if self._italic is None else self._italic
        )
        self.font.setUnderline(
            default.underline if self._underline is None else self._underline
        )
        if hasattr(self._element, "setDefaultFont"):
            self._element.setDefaultFont(self.font)
        elif hasattr(self._element, "setFont"):
            self._element.setFont(self.font)
        self.onSelectionChange()

    def onSelectionChange(self : Self) -> None:
        self.color = self.selected if self._element.isSelected() else self.normal
        if hasattr(self._element, "setDefaultTextColor"):
            self._element.setDefaultTextColor(self.color)
        elif hasattr(self._element, "setColor"):
            self._element.setColor(self.color)

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement("text")
        xw.writeAttribute( "color",     val2str( self.color             ))
        xw.writeAttribute( "family",    val2str( self.font.family()     ))
        xw.writeAttribute( "size",      val2str( self.font.pointSizeF() ))
        xw.writeAttribute( "bold",      val2str( self.font.bold()       ))
        xw.writeAttribute( "italic",    val2str( self.font.italic()     ))
        xw.writeAttribute( "underline", val2str( self.font.underline()  ))
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        attributes = xr.attributes()
        xr.readNext()
        element_text : TextColorFont = cls()
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

class OutlinePen:
    pen : QPen

    def __init__(self : Self) -> None:
        self.pen = QPen()
        self.onSettingsChange()

    def onSettingsChange(self : Self) -> None:
        self.pen.setColor(hub.settings.getTheme("selected/line"))
        self.pen.setWidthF(hub.settings.get("display/outline/width"))
        self.pen.setStyle(hub.settings.get("display/outline/style"))

class Appearance:
    _element : "Element"
    line     : LinePen
    fill     : FillBrush
    text     : TextColorFont
    outline  : OutlinePen

    def __init__(
        self     : Self,
        element  : "Element",
        has_line : bool = False,
        has_fill : bool = False,
        has_text : bool = False
    ) -> None:
        self._element = element
        self.line = LinePen(element) if has_line else None
        self.fill = FillBrush(element) if has_fill else None
        self.text = TextColorFont(element) if has_text else None
        self.outline = OutlinePen()
        self.onSettingsChange()
        hub.settings.change.connect(self.onSettingsChange)

    def onSettingsChange(self : Self) -> None:
        if self.line:
            self.line.onSettingsChange()
        if self.fill:
            self.fill.onSettingsChange()
        if self.text:
            self.text.onSettingsChange()
        self.outline.onSettingsChange()

    def onSelectionChange(self : Self) -> None:
        if self.line:
            self.line.onSelectionChange()
        if self.fill:
            self.fill.onSelectionChange()
        if self.text:
            self.text.onSelectionChange()

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
        element_settings : Appearance = cls()
        while not xr.atEnd():
            if xr.isEndElement() and xr.name() == "settings":
                break
            if xr.isStartElement():
                match xr.name():
                    case "line":
                        element_settings.line = LinePen.fromXml(xr)
                    case "fill":
                        element_settings.fill = FillBrush.fromXml(xr)
                    case "text":
                        element_settings.text = TextColorFont.fromXml(xr)
        xr.readNext()
        return element_settings

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

    appearance : Appearance

    def __init__(
        self     : Self,
        has_line : bool = False,
        has_fill : bool = False,
        has_text : bool = False
    ) -> None:
        # TODO change to has_line, has_fill, has_text
        self.appearance = Appearance(self, has_line, has_fill, has_text)
        self.setZValue(self.Z)
        f = QGraphicsItem.GraphicsItemFlag
        self.setFlag( f.ItemIsSelectable              , True )
        self.setFlag( f.ItemSendsGeometryChanges      , True  )
        self.setFlag( f.ItemSendsScenePositionChanges , True  )
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)
        self.setSelected(True)

    def itemChange(
        self   : Self,
        change : QGraphicsItem.GraphicsItemChange,
        value  : Any
    ) -> Any:
        if change == self.GraphicsItemChange.ItemSelectedHasChanged:
            self.appearance.onSelectionChange()
        return super().itemChange(change, value)

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement(self.__class__.__name__)
        self.appearance.toXml(xw)
        toXmlAttrs(self, xw)
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr: QXmlStreamReader) -> Self:
        instance = cls()
        instance.settings = Appearance.fromXml(xr)
        fromXmlAttrs(instance, xr)
        return instance

class cmdElement(QUndoCommand):
    """Base class for all commands that work with an element."""
    scene   : "Drawing"
    element : Element

    def __init__(
        self    : Self,
        scene   : "Drawing",
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
        scene    : "Drawing",
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
    has_line : bool
    has_fill : bool
    has_text : bool

    def __init__(
        self       : Self,
        scene      : "Drawing",
        element    : Element
    ):
        super().__init__(scene, element)

    def id(self : Self) -> int:
            """Return a unique ID for merging commands."""
            element_id = id(self.element) & 0x7FFFFFFF
            class_id = hash(self.__class__.__name__) & 0x7FFFFFFF
            return ((element_id + class_id) & 0x7FFFFFFF)

    def mergeWith(self : Self, other : QUndoCommand) -> bool:
        if not super().mergeWith(other):
            return False
        return True

    def redo(self : Self) -> None:
        """Add or update the element in the scene."""
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
        scene    : "Drawing",
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

__all__ = ["Element"]
from .key_point import KPLoc, KeyPoint, KPDef, KPManager
__all__ += key_point.__all__
from .rectangle import Rectangle, cmdPlaceRectangle
__all__ += rectangle.__all__
from .text_block import TextBlock, cmdPlaceTextBlock
__all__ += text_block.__all__
from .symbol_instance import SymbolInstance
__all__ += symbol_instance.__all__
from .block import Block
__all__ += block.__all__

element_class_dict = {}
for class_name in __all__:
    element_class_dict[class_name] = globals()[class_name]
__all__ += ["element_class_dict"]
