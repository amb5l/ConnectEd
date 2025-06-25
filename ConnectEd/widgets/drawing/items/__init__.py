import uuid

from typing      import Self, Optional, Any
from types       import SimpleNamespace
from dataclasses import dataclass

from PyQt6.QtCore    import Qt, QXmlStreamWriter, QXmlStreamReader, QPointF
from PyQt6.QtGui     import QPen, QBrush, QColor, QFont, QAction, QUndoCommand
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem, \
                            QApplication, QGraphicsSceneContextMenuEvent, QMenu

from ....core import logger, \
                     val2str, str2val, camel_to_proper, toXmlAttrs, fromXmlAttrs

from .... import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene

class Default:
    def __str__(self): return "default"
    def __repr__(self): return "<default>"

DEFAULT = Default()

class NoChange:
    def __str__(self): return "no change"
    def __repr__(self): return "<no change>"

NO_CHANGE = NoChange()

@dataclass
class LineSpec:
    color : QColor
    width : float
    style : Qt.PenStyle

@dataclass
class LinePref:
    color : Default | QColor      = DEFAULT
    width : Default | float       = DEFAULT
    style : Default | Qt.PenStyle = DEFAULT

    def toStr(self):
        s_c = "default" if self.color is DEFAULT else \
            hex(self.color.rgba())
        s_w = "default" if self.width is DEFAULT else \
            str(self.width)
        s_s = "default" if self.style is DEFAULT else \
            str(self.style).replace("PenStyle.", "")
        return f"{s_c},{s_w},{s_s}"

    @classmethod
    def fromStr(cls, s : str) -> Self:
        s_c, s_w, s_s = s.split(",")
        color = DEFAULT if s_c == "default" else QColor(int(s_c, 16))
        width = DEFAULT if s_w == "default" else float(s_w)
        style = DEFAULT if s_s == "default" else Qt.PenStyle[s_s]
        return cls(color, width, style)

@dataclass
class LinePrefDefault:
    color : Optional[ Default | QColor      ] = None
    width : Optional[ Default | float       ] = None
    style : Optional[ Default | Qt.PenStyle ] = None

@dataclass
class LinePrefChange:
    color : Optional[ NoChange | Default | QColor      ] = None
    width : Optional[ NoChange | Default | float       ] = None
    style : Optional[ NoChange | Default | Qt.PenStyle ] = None

@dataclass
class FillSpec:
    color : QColor
    style : Qt.BrushStyle

@dataclass
class FillPref:
    color : Default | QColor        = DEFAULT
    style : Default | Qt.BrushStyle = DEFAULT

    def toStr(self):
        s_c = "default" if self.color is DEFAULT else \
            hex(self.color.rgba())
        s_s = "default" if self.style is DEFAULT else \
            str(self.style).replace("BrushStyle.", "")
        return f"{s_c},{s_s}"

    @classmethod
    def fromStr(cls, s : str) -> Self:
        s_c, s_s = s.split(",")
        color = DEFAULT if s_c == "default" else QColor(int(s_c, 16))
        style = DEFAULT if s_s == "default" else Qt.BrushStyle[s_s]
        return cls(color, style)

@dataclass
class FillPrefDefault:
    color : Optional[ Default | QColor        ] = None
    style : Optional[ Default | Qt.BrushStyle ] = None

@dataclass
class FillPrefChange:
    color : Optional[ NoChange | Default | QColor        ] = None
    style : Optional[ NoChange | Default | Qt.BrushStyle ] = None

@dataclass
class TextSpec:
    color     : QColor
    family    : str
    size      : float
    bold      : bool
    italic    : bool
    underline : bool

@dataclass
class TextPref:
    color     : Default | QColor = DEFAULT
    family    : Default | str    = DEFAULT
    size      : Default | float  = DEFAULT
    bold      : Default | bool   = DEFAULT
    italic    : Default | bool   = DEFAULT
    underline : Default | bool   = DEFAULT

    def toStr(self):
        s_c = "default" if self.color is DEFAULT else \
            hex(self.color.rgba())
        s_f = "default" if self.family is DEFAULT else \
            self.family
        s_s = "default" if self.size is DEFAULT else \
            str(self.size)
        s_b = "default" if self.bold is DEFAULT else \
            str(self.bold)
        s_i = "default" if self.italic is DEFAULT else \
            str(self.italic)
        s_u = "default" if self.underline is DEFAULT else \
            str(self.underline)
        return f"{s_c},{s_f},{s_s},{s_b},{s_i},{s_u}"

    @classmethod
    def fromStr(cls, s : str) -> Self:
        s_c, s_f, s_s, s_b, s_i, s_u = s.split(",")
        color     = DEFAULT if s_c == "default" else QColor(int(s_c, 16))
        family    = DEFAULT if s_f == "default" else s_f
        size      = DEFAULT if s_s == "default" else float(s_s)
        bold      = DEFAULT if s_b == "default" else s_b.lower() == "true"
        italic    = DEFAULT if s_i == "default" else s_i.lower() == "true"
        underline = DEFAULT if s_u == "default" else s_u.lower() == "true"
        return cls(color, family, size, bold, italic, underline)

@dataclass
class TextPrefDefault:
    color     : Optional[ Default | QColor ] = None
    family    : Optional[ Default | str    ] = None
    size      : Optional[ Default | float  ] = None
    bold      : Optional[ Default | bool   ] = None
    italic    : Optional[ Default | bool   ] = None
    underline : Optional[ Default | bool   ] = None

@dataclass
class TextPrefChange:
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
class AppearancePref:
    line : Optional[LinePref] = None
    fill : Optional[FillPref] = None
    text : Optional[TextPref] = None

@dataclass
class AppearancePrefChange:
    line : Optional[LinePrefChange] = None
    fill : Optional[FillPrefChange] = None
    text : Optional[TextPrefChange] = None

class LinePen:
    element  : "ElementMixin"
    color    : Default | QColor
    width    : Default | float
    style    : Default | Qt.PenStyle
    normal   : QPen
    selected : QPen
    pen      : QPen

    def __init__(
        self    : Self,
        element : "ElementMixin",
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

    def setPref(self : Self, c : LinePref | LinePrefChange) -> None:
        if c.color is not NO_CHANGE: self.color = c.color
        if c.width is not NO_CHANGE: self.width = c.width
        if c.style is not NO_CHANGE: self.style = c.style
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
    element  : "ElementMixin"
    color    : Default | QColor
    style    : Default | Qt.BrushStyle
    normal   : QBrush
    selected : QBrush
    brush    : QBrush

    def __init__(
        self    : Self,
        element : "ElementMixin",
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

    def setPref(self : Self, c : FillPref | FillPrefChange) -> None:
        if c.color is not NO_CHANGE: self.color = c.color
        if c.style is not NO_CHANGE: self.style = c.style
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
    element   : "ElementMixin"
    color     : Default | QColor
    family    : Default | str
    size      : Default | float
    bold      : Default | bool
    italic    : Default | bool
    underline : Default | bool
    normal    : QColor
    selected  : QColor
    current   : QColor
    font      : QFont

    def __init__(
        self    : Self,
        element : "ElementMixin",
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

    def setPref(self : Self, c : TextPref | TextPrefChange) -> None:
        if c.color     is not NO_CHANGE: self.color     = c.color
        if c.family    is not NO_CHANGE: self.family    = c.family
        if c.size      is not NO_CHANGE: self.size      = c.size
        if c.bold      is not NO_CHANGE: self.bold      = c.bold
        if c.italic    is not NO_CHANGE: self.italic    = c.italic
        if c.underline is not NO_CHANGE: self.underline = c.underline
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
        self.current = self.selected if self.element.isSelected() else self.normal
        if hasattr(self.element, "setDefaultTextColor"):
            self.element.setDefaultTextColor(self.current)
        elif hasattr(self.element, "setColor"):
            self.element.setColor(self.current)

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
            v = attr.value()
            match attr.name():
                case "color"     : element_text.setColor(str2val(v, QColor))
                case "family"    : element_text.setFamily(str2val(v, str))
                case "size"      : element_text.setSize(str2val(v, float))
                case "bold"      : element_text.setBold(str2val(v, bool))
                case "italic"    : element_text.setItalic(str2val(v, bool))
                case "underline" : element_text.setUnderline(str2val(v, bool))
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
    _MENU = None # class context menu

    _instance : Optional[Self]

    def itemChange(
        self: QGraphicsItem,
        change: QGraphicsItem.GraphicsItemChange,
        value: Any
    ) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            if hasattr(self, 'onSelectionChange'):
                self.onSelectionChange()
        return super().itemChange(change, value)

    @staticmethod
    def getMenu(cls) -> QMenu:
        if cls._MENU is None:
            cls._MENU = QMenu()
            for item_name in cls._MENU_ITEM_NAMES:
                if item_name.startswith("-"):
                    cls._MENU.addSeparator()
                else:
                    action = QAction(item_name, cls._MENU)
                    action.triggered.connect(lambda: None)  # placeholder
                    cls._MENU.addAction(action)
        return cls._MENU

    def contextMenuEvent(
        self  : Self,
        event : QGraphicsSceneContextMenuEvent
    ) -> None:
        from .. import DrawingView
        widget = QApplication.widgetAt(event.screenPos())
        while widget is not None and widget.parent() is not None:
            if isinstance(widget, DrawingView):
                break
            widget = widget.parent()
        self._instance = self
        for action in self._menu.actions():
            slot_name = \
                f"ctxMenu{action.text().replace(' ', '').replace('.', '')}"
            slot = getattr(self, slot_name, None)
            if slot:
                try:
                    action.triggered.disconnect()
                except TypeError:
                    pass
                action.triggered.connect(
                    lambda checked=False, w=widget: slot(self._instance, w)
                )
        self._menu.exec(event.screenPos())
        self._instance = None

class CustomGraphicsItem(CustomGraphicsItemMixin, QGraphicsItem):
    pass

class CustomGraphicsRectItem(CustomGraphicsItemMixin, QGraphicsRectItem):
    pass

class CustomGraphicsTextItem(CustomGraphicsItemMixin, QGraphicsTextItem):
    pass

class ElementMixin:
    """Mixin class for all elements."""

    _XML_ATTRS = {
        "uuid" : "str",
        "pos" : (
            "QPointF", True,
            lambda self, value: self.setPos(value),
            lambda self: self.pos()
        ),
        "line" : (
            "LinePref", False,
            lambda self, value: self.line.setPref(value),
            lambda self: self.line.getPref()
        ),
        "fill" : (
            "FillPref", False,
            lambda self, value: self.fill.setPref(value),
            lambda self: self.fill.getPref()
        ),
        "text" : (
            "TextPref", False,
            lambda self, value: self.text.setPref(value),
            lambda self: self.text.getPref()
        )
    }
    _MENU = None

    uuid    : str
    line    : Optional[LinePen]
    fill    : Optional[FillBrush]
    text    : Optional[TextColorFont]
    outline : OutlinePen
    _menu   : QMenu

    def initElement(
        self : Self,
        line : Optional[LinePref] = None,
        fill : Optional[FillPref] = None,
        text : Optional[TextPref] = None
    ) -> None:
        self.resetUuid()
        if line is not None:
            self.line = LinePen(self, line)
        if fill is not None:
            self.fill = FillBrush(self, fill)
        if text is not None:
            self.text = TextColorFont(self, text)
        self.outline = OutlinePen()
        self.setZValue(self.Z)
        f = QGraphicsItem.GraphicsItemFlag
        self.setFlag( f.ItemIsSelectable              , True )
        self.setFlag( f.ItemSendsGeometryChanges      , True  )
        self.setFlag( f.ItemSendsScenePositionChanges , True  )
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)
        hub.settings.change.connect(self.onSettingsChange)
        self._menu = CustomGraphicsItemMixin.getMenu(self.__class__)

    def __hash__(self):
        return hash(self.uuid)

    def __eq__(self, other):
        if not isinstance(other, ElementMixin):
            return NotImplemented
        return self.uuid == other.uuid

    def onSettingsChange(self : Self) -> None:
        if hasattr(self, "line"): self.line.onSettingsChange()
        if hasattr(self, "fill"): self.fill.onSettingsChange()
        if hasattr(self, "text"): self.text.onSettingsChange()
        self.outline.onSettingsChange()

    def onSelectionChange(self : Self) -> None:
        if hasattr(self, "line"): self.line.onSelectionChange()
        if hasattr(self, "fill"): self.fill.onSelectionChange()
        if hasattr(self, "text"): self.text.onSelectionChange()

    def resetUuid(self : Self) -> None:
        self.uuid = str(uuid.uuid4())

    def getDefaults(self : Self) -> SimpleNamespace:
        r = SimpleNamespace()
        if hasattr(self, "line"): r.line = self.line.getDefaults()
        if hasattr(self, "fill"): r.fill = self.fill.getDefaults()
        if hasattr(self, "text"): r.text = self.text.getDefaults()
        return r

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement(self.__class__.__name__)
        toXmlAttrs(self, xw)
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr: QXmlStreamReader) -> Self:
        instance = cls()
        fromXmlAttrs(instance, xr)
        instance.setKPVisible(False)  # Ensure keypoints are hidden
        return instance

    def clone(self : Self) -> Self:
        """Create a clone of this element with a new UUID."""
        # Create a new instance of the same class
        clone = self.__class__()
        # Copy position
        clone.setPos(self.pos())
        # Copy appearance preferences if they exist
        if hasattr(self, "line"):
            setattr(clone, "line", LinePen(clone, self.line.getPref()))
        if hasattr(self, "fill"):
            setattr(clone, "fill", FillBrush(clone, self.fill.getPref()))
        if hasattr(self, "text"):
            setattr(clone, "text", TextColorFont(clone, self.text.getPref()))
        # New UUID is automatically assigned in __init2__() via resetUuid()
        return clone

class cmdElement(QUndoCommand):
    """Base class for all commands that work with an element."""
    scene   : "DrawingScene"
    element : ElementMixin

    def __init__(
        self    : Self,
        scene   : "DrawingScene",
        element : ElementMixin
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
    elements : list[ElementMixin]

    def __init__(
        self     : Self,
        scene    : "DrawingScene",
        elements : list[ElementMixin]
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

    def redo(self : Self) -> None:
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement redo"
        )

    def undo(self : Self) -> None:
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement undo"
        )

class cmdPlaceElement(cmdElement):
    """Base class for all commands that place an element."""

    def __init__(
        self    : Self,
        scene   : "DrawingScene",
        element : ElementMixin
    ):
        super().__init__(scene, element) # record scene and element instances

    def redo(self : Self) -> None:
        if self.element.scene() != self.scene:
            self.scene.addItem(self.element)

    def undo(self : Self) -> None:
        self.scene.removeItem(self.element)

def clone(elements : list[ElementMixin]) -> list[ElementMixin]:
    r = []
    for element in elements:
        try:
            r.append(element.clone())
        except Exception as e:
            logger.warning(f"Failed to clone element {element}: {e}")
    return r

__all__ = [
    "Default",
    "DEFAULT",
    "NoChange",
    "NO_CHANGE",
    "LineSpec",
    "LinePref",
    "LinePrefChange",
    "FillSpec",
    "FillPref",
    "FillPrefChange",
    "TextSpec",
    "TextPref",
    "TextPrefChange",
    "AppearanceSpec",
    "AppearancePref",
    "AppearancePrefChange",
    "CustomGraphicsItem",
    "CustomGraphicsRectItem",
    "CustomGraphicsTextItem",
    "ElementMixin",
    "cmdElement",
    "cmdElements",
    "cmdPlaceElement",
    "clone"
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
