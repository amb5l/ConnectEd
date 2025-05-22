import uuid

from typing      import Self, Optional, Any
from types       import SimpleNamespace
from dataclasses import dataclass

from PyQt6.QtCore    import Qt, QXmlStreamWriter, QXmlStreamReader, QPointF
from PyQt6.QtGui     import QPen, QBrush, QColor, QFont, QUndoCommand, \
                            QFontDatabase
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem

from ....core import val2str, str2val, camel_to_proper, toXmlAttrs, fromXmlAttrs

from .... import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene

class Default:
    def __str__(self): return "default"
    def __repr__(self): return "<default>"

DEFAULT = Default()

class NoChange:
    def __str__(self): return "No Change"
    def __repr__(self): return "<no change>"

NO_CHANGE = NoChange()

@dataclass
class LineSpec:
    color : Optional[QColor]      = None
    width : Optional[float]       = None
    style : Optional[Qt.PenStyle] = None

@dataclass
class LineSpecDelta:
    color : Optional[ NoChange | QColor      ] = None
    width : Optional[ NoChange | float       ] = None
    style : Optional[ NoChange | Qt.PenStyle ] = None

@dataclass
class LinePref:
    color : Optional[ Default | QColor      ] = DEFAULT
    width : Optional[ Default | float       ] = DEFAULT
    style : Optional[ Default | Qt.PenStyle ] = DEFAULT

@dataclass
class LineChoice:
    color : Optional[ NoChange | Default | QColor      ] = None
    width : Optional[ NoChange | Default | float       ] = None
    style : Optional[ NoChange | Default | Qt.PenStyle ] = None

@dataclass
class FillSpec:
    color : Optional[QColor]
    style : Qt.BrushStyle

@dataclass
class FillSpecDelta:
    color : Optional[ NoChange | QColor        ] = None
    style : Optional[ NoChange | Qt.BrushStyle ] = None

@dataclass
class FillPref:
    color : Optional[ Default | QColor        ] = DEFAULT
    style : Optional[ Default | Qt.BrushStyle ] = DEFAULT

@dataclass
class FillChoice:
    color : Optional[ NoChange | Default | QColor        ] = None
    style : Optional[ NoChange | Default | Qt.BrushStyle ] = None

@dataclass
class TextSpec:
    color     : Optional[QColor] = None
    family    : Optional[str]    = None
    size      : Optional[float]  = None
    bold      : Optional[bool]   = None
    italic    : Optional[bool]   = None
    underline : Optional[bool]   = None

@dataclass
class TextSpecDelta:
    color     : Optional[ NoChange | QColor   ] = None
    family    : Optional[ NoChange | str      ] = None
    size      : Optional[ NoChange | float    ] = None
    bold      : Optional[ NoChange | bool     ] = None
    italic    : Optional[ NoChange | bool     ] = None
    underline : Optional[ NoChange | bool     ] = None

@dataclass
class TextPref:
    color     : Optional[ Default | QColor   ] = DEFAULT
    family    : Optional[ Default | str      ] = DEFAULT
    size      : Optional[ Default | float    ] = DEFAULT
    bold      : Optional[ Default | bool     ] = DEFAULT
    italic    : Optional[ Default | bool     ] = DEFAULT
    underline : Optional[ Default | bool     ] = DEFAULT

@dataclass
class TextChoice:
    color     : Optional[ NoChange | Default | QColor ] = None
    family    : Optional[ NoChange | Default | str    ] = None
    size      : Optional[ NoChange | Default | float  ] = None
    bold      : Optional[ NoChange | Default | bool   ] = None
    italic    : Optional[ NoChange | Default | bool   ] = None
    underline : Optional[ NoChange | Default | bool   ] = None

@dataclass
class AppearanceSpec:
    line : Optional[LineSpec] = None
    fill : Optional[FillSpec] = None
    text : Optional[TextSpec] = None

@dataclass
class AppearanceSpecDelta:
    line : Optional[LineSpecDelta] = None
    fill : Optional[FillSpecDelta] = None
    text : Optional[TextSpecDelta] = None

@dataclass
class AppearancePref:
    line : Optional[LinePref] = None
    fill : Optional[FillPref] = None
    text : Optional[TextPref] = None

@dataclass
class AppearanceChoice:
    line : Optional[LineChoice] = None
    fill : Optional[FillChoice] = None
    text : Optional[TextChoice] = None

class LinePen:
    element  : "Element"
    color    : Default | QColor
    width    : Default | float
    style    : Default | Qt.PenStyle
    normal   : QPen
    selected : QPen
    pen      : QPen

    def __init__(
        self    : Self,
        element : "Element",
        pref    : LinePref = LinePref(DEFAULT, DEFAULT, DEFAULT)
    ) -> None:
        self.element  = element
        self.color    = pref.color
        self.width    = pref.width
        self.style    = pref.style
        self.normal   = QPen()
        self.selected = QPen()
        self.onSettingsChange()

    def getPref(self : Self) -> LinePref:
        return LinePref(self.color, self.width, self.style)

    def setPref(self : Self, pref : LinePref) -> None:
        self.color = pref.color
        self.width = pref.width
        self.style = pref.style
        self.onSettingsChange()

    def getDefaults(self : Self) -> SimpleNamespace:
        element_name = self.element.__class__.__name__
        r = hub.settings.get(f"defaults/elements/{element_name}/line")
        r.color = hub.settings.getTheme(f"elements/{element_name}/line")
        return r

    def onSettingsChange(self : Self) -> None:
        default = self.getDefaults()
        color_normal = default.color if self.color is DEFAULT else self.color
        color_selected = hub.settings.getTheme("selected/line")
        width = default.width if self.width is DEFAULT else self.width
        style = default.style if self.style is DEFAULT else self.style
        self.normal.setColor(color_normal)
        self.normal.setWidthF(width)
        self.normal.setStyle(style)
        self.selected.setColor(color_selected)
        self.selected.setWidthF(width)
        self.selected.setStyle(style)
        self.onSelectionChange()

    def onSelectionChange(self : Self) -> None:
        self.pen = self.selected if self.element.isSelected() else self.normal

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement("line")
        xw.writeAttribute("color", val2str(self.color))
        xw.writeAttribute("width", val2str(self.width))
        xw.writeAttribute("style", val2str(self.style))
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        attributes = xr.attributes()
        xr.readNext()
        inst : LinePen = cls()
        for attr in attributes:
            match attr.name():
                case "color":
                    inst.setColor(str2val(attr.value(), QColor))
                case "width":
                    inst.setWidth(str2val(attr.value(), float))
                case "style":
                    inst.setStyle(str2val(attr.value(), Qt.PenStyle))
        return inst

class FillBrush:
    element  : "Element"
    color    : Default | QColor
    style    : Default | Qt.BrushStyle
    normal   : QBrush
    selected : QBrush
    brush    : QBrush

    def __init__(
        self    : Self,
        element : "Element",
        pref    : FillPref = FillPref(DEFAULT, DEFAULT)
    ) -> None:
        self.element  = element
        self.color    = pref.color
        self.style    = pref.style
        self.normal   = QBrush()
        self.selected = QBrush()
        self.onSettingsChange()

    def getPref(self : Self) -> FillPref:
        return FillPref(self.color, self.style)

    def setPref(self : Self, pref : FillPref) -> None:
        self.color = pref.color
        self.style = pref.style
        self.onSettingsChange()

    def getColor(self : Self) -> QColor:
        return self.color

    def setColor(self  : Self, color : QColor) -> None:
        self.color = color
        self.onSettingsChange()

    def getStyle(self : Self) -> Qt.BrushStyle:
        return self.style

    def setStyle(self  : Self, style : Qt.BrushStyle) -> None:
        self.style = style
        self.onSettingsChange()

    def getDefaults(self : Self) -> SimpleNamespace:
        r = SimpleNamespace()
        element_name = self.element.__class__.__name__
        r.style = hub.settings.get(f"defaults/elements/{element_name}/fill")
        r.color = hub.settings.getTheme(f"elements/{element_name}/fill")
        return r

    def onSettingsChange(self : Self) -> None:
        default = self.getDefaults()
        color_normal = default.color if self.color is DEFAULT else self.color
        color_selected = hub.settings.getTheme("selected/fill")
        style = default.style if self.style is DEFAULT else self.style
        self.normal.setColor(color_normal)
        self.normal.setStyle(style)
        self.selected.setColor(color_selected)
        self.selected.setStyle(style)
        self.onSelectionChange()

    def onSelectionChange(self : Self) -> None:
        self.brush = self.selected if self.element.isSelected() else self.normal

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement("fill")
        xw.writeAttribute("color", val2str(self.color))
        xw.writeAttribute("style", val2str(self.style))
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        attributes = xr.attributes()
        xr.readNext()
        inst : FillBrush = cls()
        for attr in attributes:
            match attr.name():
                case "color":
                    inst.setColor(str2val(attr.value(), QColor))
                case "style":
                    inst.setStyle(str2val(attr.value(), Qt.BrushStyle))
        return inst

class TextColorFont:
    element   : "Element"
    color     : Default | QColor
    family    : Default | str
    size      : Default | float
    bold      : Default | bool
    italic    : Default | bool
    underline : Default | bool
    normal    : QColor
    selected  : QColor
    color     : QColor
    font      : QFont

    def __init__(
        self    : Self,
        element : "Element",
        pref    : TextPref = \
                  TextPref(DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT)
    ) -> None:
        self.element   = element
        self.color     = pref.color
        self.family    = pref.family
        self.size      = pref.size
        self.bold      = pref.bold
        self.italic    = pref.italic
        self.underline = pref.underline
        self.normal    = QColor()
        self.selected  = QColor()
        self.font      = QFont()
        self.onSettingsChange()

    def getPref(self : Self) -> TextPref:
        return TextPref(
            self.color,
            self.family,
            self.size,
            self.bold,
            self.italic,
            self.underline
        )

    def setPref(self : Self, pref : TextPref) -> None:
        self.color     = pref.color
        self.family    = pref.family
        self.size      = pref.size
        self.bold      = pref.bold
        self.italic    = pref.italic
        self.underline = pref.underline
        self.onSettingsChange()

    def getDefaults(self : Self) -> SimpleNamespace:
        element_name = self.element.__class__.__name__
        r = hub.settings.get(f"defaults/elements/{element_name}/text")
        r.color = hub.settings.getTheme(f"elements/{element_name}/text")
        return r

    def onSettingsChange(self : Self) -> None:
        default = self.getDefaults()
        self.selected.setRgb(hub.settings.getTheme("selected/text").rgb())
        self.normal.setRgb(
            default.color.rgb() if self.color is DEFAULT else self.color.rgb()
        )
        self.font.setFamily(
            default.family if self.family is DEFAULT else self.family
        )
        self.font.setPointSizeF(
            default.size if self.size is DEFAULT else self.size
        )
        self.font.setBold(
            default.bold if self.bold is DEFAULT else self.bold
        )
        self.font.setItalic(
            default.italic if self.italic is DEFAULT else self.italic
        )
        self.font.setUnderline(
            default.underline if self.underline is DEFAULT else self.underline
        )
        if hasattr(self.element, "setDefaultFont"):
            self.element.setDefaultFont(self.font)
        elif hasattr(self.element, "setFont"):
            self.element.setFont(self.font)
        self.onSelectionChange()

    def onSelectionChange(self : Self) -> None:
        self.color = self.selected if self.element.isSelected() else self.normal
        if hasattr(self.element, "setDefaultTextColor"):
            self.element.setDefaultTextColor(self.color)
        elif hasattr(self.element, "setColor"):
            self.element.setColor(self.color)

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement("text")
        xw.writeAttribute( "color",     val2str( self.color     ))
        xw.writeAttribute( "family",    val2str( self.family    ))
        xw.writeAttribute( "size",      val2str( self.size      ))
        xw.writeAttribute( "bold",      val2str( self.bold      ))
        xw.writeAttribute( "italic",    val2str( self.italic    ))
        xw.writeAttribute( "underline", val2str( self.underline ))
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


class CustomGraphicsItemMixin:
    """Mixin for custom graphics items, providing hashability and itemChange."""
    _id: str

    def __hash__(self: Self) -> int:
        return hash(self._id)

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, CustomGraphicsItemMixin):
            return NotImplemented
        return self._id == other._id

    def itemChange(
        self: QGraphicsItem,
        change: QGraphicsItem.GraphicsItemChange,
        value: Any
    ) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            if hasattr(self, 'onSelectionChange'):
                self.onSelectionChange()
        return super().itemChange(change, value)

class CustomGraphicsItem(CustomGraphicsItemMixin, QGraphicsItem):
    def __init__(self: Self) -> None:
        super().__init__()
        self._id = str(uuid.uuid4())

class CustomGraphicsRectItem(CustomGraphicsItemMixin, QGraphicsRectItem):
    def __init__(self: Self) -> None:
        super().__init__()
        self._id = str(uuid.uuid4())

class CustomGraphicsTextItem(CustomGraphicsItemMixin, QGraphicsTextItem):
    def __init__(self: Self, text: str = "") -> None:
        super().__init__(text)
        self._id = str(uuid.uuid4())

class Element:
    """Mixin class for all elements."""
    XML_ATTRS = {
        "pos" : (
            "QPointF",
            lambda self, value: self.setPos(value),
            lambda self: self.pos()
        ),
        "line" : (
            "LinePref",
            lambda self, value: self.line.setPref(value),
            lambda self: self.line.getPref()
        ),
        "fill" : (
            "FillPref",
            lambda self, value: self.fill.setPref(value),
            lambda self: self.fill.getPref()
        ),
        "text" : (
            "TextPref",
            lambda self, value: self.text.setPref(value),
            lambda self: self.text.getPref()
        )
    }

    line    : Optional[LinePen]
    fill    : Optional[FillBrush]
    text    : Optional[TextColorFont]
    outline : OutlinePen

    def __init2__(
        self : Self,
        line : Optional[LinePref] = LinePref(), # all defaults
        fill : Optional[FillPref] = FillPref(), # all defaults
        text : Optional[TextPref] = TextPref()  # all defaults
    ) -> None:
        self.line    = LinePen(self, line)       if line is not None else None
        self.fill    = FillBrush(self, fill)     if fill is not None else None
        self.text    = TextColorFont(self, text) if text is not None else None
        self.outline = OutlinePen()
        self.setZValue(self.Z)
        f = QGraphicsItem.GraphicsItemFlag
        self.setFlag( f.ItemIsSelectable              , True )
        self.setFlag( f.ItemSendsGeometryChanges      , True  )
        self.setFlag( f.ItemSendsScenePositionChanges , True  )
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)
        self.setSelected(True)
        hub.settings.change.connect(self.onSettingsChange)

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, other):
        if not isinstance(other, Element):
            return NotImplemented
        return self._id == other._id

    def onSettingsChange(self : Self) -> None:
        if self.line: self.line.onSettingsChange()
        if self.fill: self.fill.onSettingsChange()
        if self.text: self.text.onSettingsChange()
        self.outline.onSettingsChange()

    def onSelectionChange(self : Self) -> None:
        if self.line: self.line.onSelectionChange()
        if self.fill: self.fill.onSelectionChange()
        if self.text: self.text.onSelectionChange()

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement(self.__class__.__name__)
        toXmlAttrs(self, xw)
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr: QXmlStreamReader) -> Self:
        instance = cls()
        fromXmlAttrs(instance, xr)
        return instance

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

class cmdElements(QUndoCommand):
    """Base class for all commands that work with multiple elements."""
    scene    : "DrawingScene"
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

    def __init__(
        self    : Self,
        scene   : "DrawingScene",
        element : Element
    ):
        super().__init__(scene, element) # record scene and element instances

    def redo(self : Self) -> None:
        if self.element.scene() != self.scene:
            self.scene.addItem(self.element)

    def undo(self : Self) -> None:
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
    "Default",
    "DEFAULT",
    "NoChange",
    "NO_CHANGE",
    "LineSpec",
    "LineSpecDelta",
    "LinePref",
    "LineChoice",
    "FillSpec",
    "FillSpecDelta",
    "FillPref",
    "FillChoice",
    "TextSpec",
    "TextSpecDelta",
    "TextPref",
    "TextChoice",
    "AppearanceSpec",
    "AppearanceSpecDelta",
    "AppearancePref",
    "AppearanceChoice",
    "CustomGraphicsItem",
    "CustomGraphicsRectItem",
    "CustomGraphicsTextItem",
    "Element",
    "cmdElement",
    "cmdElements",
    "cmdPlaceElement",
    "cmdMove",
    "cmdSlide"
]
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
