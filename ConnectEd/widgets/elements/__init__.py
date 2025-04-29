from dataclasses import dataclass
from enum        import Enum
from typing      import Self, Optional
from collections import namedtuple
from types       import SimpleNamespace

from PyQt6.QtCore    import Qt, QXmlStreamWriter, QXmlStreamReader, QPointF
from PyQt6.QtGui     import QPen, QBrush, QColor, QFont, QUndoCommand
from PyQt6.QtWidgets import QGraphicsItem

from ...core import camel_to_proper, toXmlAttrs, fromXmlAttrs

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

class KeyPoint(Enum):
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
        "pen_spec"   : "PenSpec",
        "brush_spec" : "BrushSpec",
        "text_spec"  : "TextSpec",
        "pos" : (
            "QPointF",
            lambda self, value: self.setPos(value),
            lambda self: self.pos()
        )
    }

    wip : bool

    def __init__(
        self       : Self,
        pen_spec   : bool | PenSpec   = False,
        brush_spec : bool | BrushSpec = False,
        text_spec  : bool | TextSpec  = False
    ) -> None:
        self.setZValue(self.Z)
        self.setWIP(False)
        self.setPenSpec(pen_spec)
        self.setBrushSpec(brush_spec)
        self.setTextSpec(text_spec)
        f = QGraphicsItem.GraphicsItemFlag
        self.setFlag( f.ItemSendsGeometryChanges      , True  )
        self.setFlag( f.ItemSendsScenePositionChanges , True  )
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)

    def setWIP(self : Self, wip : bool) -> None:
        self.wip = wip
        self.update()

    def isWIP(self : Self) -> bool:
        return self.wip

    def getPrefs(self : Self) -> SimpleNamespace:
        element_name = self.__class__.__name__.lower()
        return getattr(hub.settings.prefs.display.elements, element_name)

    def getTheme(self : Self) -> SimpleNamespace:
        element_name = self.__class__.__name__.lower()
        if self.isSelected():
            theme = hub.settings.theme.selected
        elif self.isWIP():
            theme = hub.settings.theme.wip
        else:
            theme = getattr(hub.settings.theme, element_name)
        return theme

    def getPrefsTheme(self : Self) -> tuple[SimpleNamespace, SimpleNamespace]:
        element_name = self.__class__.__name__.lower()
        prefs = getattr(hub.settings.prefs.display.elements, element_name)
        if self.isSelected():
            theme = hub.settings.theme.selected
        elif self.isWIP():
            theme = hub.settings.theme.wip
        else:
            theme = getattr(hub.settings.theme, element_name)
        return prefs, theme

    def setPenSpec(
        self     : Self,
        pen_spec : bool | PenSpec
    ) -> None:
        if pen_spec:
            self.pen_spec = PenSpec(None, None, None) \
                if pen_spec is True else pen_spec

    def getPenSpec(self : Self) -> PenSpec:
        return self.pen_spec

    def penFromLineSpec(self : Self) -> QPen:
        if not hasattr(self, "pen_spec"):
            return QPen(Qt.PenStyle.NoPen)
        prefs, theme = self.getPrefsTheme()
        s = self.pen_spec
        color = theme.line if s.color is None else s.color
        color.setAlpha(hub.settings.prefs.display.elements.alpha)
        width = prefs.line.width if s.width is None else s.width
        style = prefs.line.style if s.style is None else s.style
        return QPen(color, width, style)

    def penFromTextSpec(self : Self) -> QPen:
        if not hasattr(self, "text_spec"):
            return QPen(Qt.PenStyle.NoPen)
        theme = self.getTheme()
        s = self.text_spec
        color = theme.text if s.color is None else s.color
        color.setAlpha(hub.settings.prefs.display.elements.alpha)
        return QPen(color, 0, Qt.PenStyle.SolidLine)

    def colorFromTextSpec(self : Self) -> QColor:
        if not hasattr(self, "text_spec"):
            return QColor(Qt.GlobalColor.black)
        theme = self.getTheme()
        s = self.text_spec
        color = theme.text if s.color is None else s.color
        color.setAlpha(hub.settings.prefs.display.elements.alpha)
        return color

    def penWidth(self : Self) -> float:
        if not hasattr(self, "pen_spec"):
            return 0
        prefs = self.getPrefs()
        s = self.pen_spec
        return prefs.line.width if s.width is None else s.width

    def setBrushSpec(
        self       : Self,
        brush_spec : bool | BrushSpec
    ) -> None:
        if brush_spec:
            self.brush_spec = BrushSpec(None, None) \
                if brush_spec is True else brush_spec

    def getBrushSpec(self : Self) -> BrushSpec:
        return self.brush_spec

    def brushFromSpec(self : Self) -> QBrush:
        if not hasattr(self, "brush_spec"):
            return QBrush(Qt.BrushStyle.NoBrush)
        prefs, theme = self.getPrefsTheme()
        s = self.brush_spec
        color = theme.fill if s.color is None else s.color
        color.setAlpha(hub.settings.prefs.display.elements.alpha)
        style = prefs.fill if s.style is None else s.style
        return QBrush(color, style)

    def setTextSpec(
        self      : Self,
        text_spec : bool | TextSpec
    ) -> None:
        if text_spec:
            self.text_spec = TextSpec(None, None, None, None, None, None) \
                if text_spec is True else text_spec

    def getTextSpec(self : Self) -> TextSpec:
        return self.text_spec

    def fontFromSpec(self : Self) -> QFont | None: # TODO: return default font?
        if not hasattr(self, "text_spec"):
            return None
        item_name = self.__class__.__name__.lower()
        prefs = getattr(hub.settings.prefs.display.elements, item_name).font
        font = QFont()
        font.setFamily(
            prefs.family if self.text_spec.family is None else
                self.text_spec.family
        )
        font.setPointSizeF(
            prefs.size if self.text_spec.size is None else
                self.text_spec.size
        )
        font.setWeight(
            prefs.weight if self.text_spec.weight is None else
                self.text_spec.weight
        )
        font.setItalic(
            prefs.italic if self.text_spec.italic is None else
                self.text_spec.italic
        )
        font.setUnderline(
            prefs.underline if self.text_spec.underline is None else
                self.text_spec.underline
        )
        return font

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement(self.__class__.__name__)
        toXmlAttrs(self, xw)

    @classmethod
    def fromXml(cls : Self, xr: QXmlStreamReader) -> Self:
        instance = cls()
        fromXmlAttrs(instance, xr)
        return instance

class ElementWithGrips(Element):
    """Base class for all elements with grips."""

    grips : dict[KeyPoint, "Grip"]

    def __init__(
        self       : Self,
        pen_spec   : bool | PenSpec   = False,
        brush_spec : bool | BrushSpec = False,
        text_spec  : bool | TextSpec  = False
    ) -> None:
        super().__init__(pen_spec, brush_spec, text_spec)
        self.grips = {kp: self.GRIP_TYPE(self, kp) for kp in self.GRIP_POINTS}
        for grip in self.grips.values():
            grip.setZValue(self.zValue() + grip.Z_DELTA)

    def getKeyPointPos(self : Self, kp : KeyPoint) -> QPointF:
        rect = self.gripsRect()
        return QPointF(kp.h * rect.width(), kp.v * rect.height())

    def updateGripsPosition(self : Self) -> None:
        for kp in self.grips.keys():
            p = self.getKeyPointPos(kp)
            self.grips[kp].setPos(p.x(), p.y())

class ElementWithAnchor(ElementWithGrips):
    """Base class for all elements with an anchor."""
    XML_ATTRS = ElementWithGrips.XML_ATTRS | {
        "anchor" : "KeyPoint"
    }

    anchor  : KeyPoint

    def __init__(
        self       : Self,
        anchor     : KeyPoint = KeyPoint.TOP_LEFT,
        pen_spec   : bool | PenSpec   = False,
        brush_spec : bool | BrushSpec = False,
        text_spec  : bool | TextSpec  = False
    ) -> None:
        super().__init__(pen_spec, brush_spec, text_spec)
        self.anchor = anchor

    def setAnchor(
        self   : Self,
        anchor : KeyPoint = KeyPoint.TOP_LEFT
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
    wip        : bool
    pen_spec   : bool | PenSpec
    brush_spec : bool | BrushSpec
    text_spec  : bool | TextSpec

    def __init__(
        self       : Self,
        scene      : "DrawingScene",
        element    : Optional[Element] = None,
        pen_spec   : bool | PenSpec   = True,
        brush_spec : bool | BrushSpec = True,
        text_spec  : bool | TextSpec  = True,
        wip        : bool = False
    ):
        if element is None:
            element_class_name = self.__class__.__name__.replace("cmdPlace", "")
            element = globals()[element_class_name]()
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
        self.element.setWIP(self.wip)
        self.element.setPenSpec(self.pen_spec)
        self.element.setBrushSpec(self.brush_spec)
        self.element.setTextSpec(self.text_spec)
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

__all__ = []

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
