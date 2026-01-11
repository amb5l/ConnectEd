# unified text item (line or block text)
# parent handles origin, position, rotation
# child handles rotation compensation

from typing import Self

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsSceneContextMenuEvent
from PyQt6.QtGui     import QColor, QFont

from ...property   import PropertySpec
from ...properties import PropertiesMixin

from .. import Default, DEFAULT, AlignH, AlignV

from ..mixin         import ItemMixin
from ..mixin.origin  import ItemOriginMixin
from ..mixin.pos     import ItemPosMixin
from ..mixin.rotate  import ItemRotateMixin
from ..mixin.handle  import ItemRectHandlesMixin
from ..mixin.quill   import ItemQuillMixin
from ..mixin.outline import ItemOutlineMixin
from ..mixin.change  import ItemChangeMixin
from ..mixin.clone   import ItemCloneMixin
from ..mixin.xml     import ItemXmlMixin
from ..mixin.menu    import ItemMenuMixin

from ..null_point import NullPoint

from .line  import UniTextLine
from .block import UniTextBlock


class UniText(
    ItemMixin,
    ItemOriginMixin,
    ItemPosMixin,
    ItemRotateMixin,
    ItemRectHandlesMixin,
    ItemQuillMixin,
    ItemOutlineMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemXmlMixin,
    ItemMenuMixin,
    PropertiesMixin,
    NullPoint
):
    """
    Text item. Supports line or block text and rotation compensation.
    """

    # class attributes
    _PROPERTY_SPECS = \
        ItemPosMixin._PROPERTY_SPECS_POS | \
        ItemRotateMixin._PROPERTY_SPECS_ROTATE | \
        {
            "Text" : PropertySpec(
                getter = lambda self: self.text(),
                setter = lambda self, value: self.setText(value)
            ),
            "AlignH" : PropertySpec(
                kind   = "AlignH",
                getter = lambda self: self.horizontalAlignment(),
                setter = lambda self, value: self.setHorizontalAlignment(value)
            ),
            "AlignV" : PropertySpec(
                kind   = "AlignV",
                valid = lambda self: self.height() is not None,
                getter = lambda self: self.verticalAlignment(),
                setter = lambda self, value: self.setVerticalAlignment(value)
            ),
            "Width" : PropertySpec(
                kind   = "float",
                valid  = lambda self: self.width() is not None,
                getter = lambda self: self.width(),
                setter = lambda self, value: self.setWidth(value)
            ),
            "Height" : PropertySpec(
                kind   = "float",
                valid  = lambda self: self.height() is not None,
                getter = lambda self: self.height(),
                setter = lambda self, value: self.setHeight(value)
            )
        } | \
        ItemQuillMixin._PROPERTY_SPECS_QUILL

    # instance attributes
    _child : UniTextLine | UniTextBlock

    def __init__(
        self      : Self,
        text      : str                  = "",
        block     : bool                 = False,
        origin    : str                  = "Top Left",
        align_h   : AlignH               = AlignH.LEFT,
        align_v   : AlignV               = AlignV.TOP,
        width     : float | None         = None,
        height    : float | None         = None,
        color     : QColor | Default     = DEFAULT,
        font      : str    | Default     = DEFAULT,
        size      : float  | Default     = DEFAULT,
        bold      : bool   | Default     = DEFAULT,
        italic    : bool   | Default     = DEFAULT,
        underline : bool   | Default     = DEFAULT,
        parent    : QGraphicsItem | None = None
    ) -> None:
        super().__init__()
        self._child = UniTextBlock() if block else UniTextLine()
        self._child.setText(text)
        self.setOrigin(origin)
        if color     : self.setQuillColor(color)
        if font      : self.setQuillFamily(font)
        if size      : self.setQuillSize(size)
        if bold      : self.setQuillBold(bold)
        if italic    : self.setQuillItalic(italic)
        if underline : self.setQuillUnderline(underline)

    def onSceneRotationChange(self : Self) -> None:
        self._child.onSceneRotationChange()

    ############################################################################
    # expose child methods

    def text(self : Self) -> str:
        return self._child.text()

    def setText(self : Self, text : str) -> None:
        self._child.setText(text)

    def alignH(self : Self) -> AlignH:
        return self._child.alignH()

    def setAlignH(self : Self, align_h : AlignH) -> None:
        self._child.setAlignH(align_h)

    def alignV(self : Self) -> AlignV:
        return self._child.alignV()

    def setAlignV(self : Self, align_v : AlignV) -> None:
        self._child.setAlignV(align_v)

    def width(self : Self) -> float | None:
        return self._child.width()

    def setWidth(self : Self, width : float) -> None:
        self._child.setWidth(width)

    def height(self : Self) -> float | None:
        return self._child.height()

    def setHeight(self : Self, height : float) -> None:
        self._child.setHeight(height)

    def color(self : Self) -> QColor:
        return self._child.color()

    def setColor(self : Self, color : QColor) -> None:
        self._child.setColor(color)

    def font(self : Self) -> QFont:
        return self._child.font()

    def setFont(self : Self, font : QFont) -> None:
        self._child.setFont(font)

    ############################################################################

    def block(self : Self) -> bool:
        return isinstance(self._child, UniTextBlock)

    def setBlock(self : Self, block : bool) -> None:
        if isinstance(self._child, UniTextLine) and block:
            new_child = UniTextBlock()
            new_child.setText(self._child.text())
            new_child.setColor(self._child.color())
            new_child.setFont(self._child.font())
            new_child.setAlignH(self._child.alignH())
            new_child.setAlignV(self._child.alignV())
            new_child.setWidth(self._child.width())
            new_child.setHeight(self._child.height())
            self._child = new_child
            raise NotImplementedError("need to convert line to block")
        elif isinstance(self._child, UniTextBlock) and not block:
            raise NotImplementedError("need to convert block to line")



    def handleRect(self : Self) -> QRectF:
        """Return the rectangle used for handles."""
        return self._brect

    def moveHandleBy(self : Self, name : str, delta : QPointF) -> None:
        """Resize/move the text as appropriate."""
        if self.isLine():
            self.moveBy(delta)
        elif self.isBlock():
            match name:
                case "Top Left":
                    self.moveBy(delta)
                    self._child.resizeBy(-delta)
                case "Top Center":
                    self.setPos(self.pos() + QPointF(0, delta.y()))
                    self._child.resizeBy(0, -delta.y())
                case "Top Right":
                    self.setPos(self.pos() + QPointF(0, delta.y()))
                    self._child.resizeBy(delta.x(), -delta.y())
                case "Middle Left":
                    self.setPos(self.pos() + QPointF(delta.x(), 0))
                    self._child.resizeBy(-delta.x(), 0)
                case "Middle Center":
                    self.moveBy(delta)
                case "Middle Right":
                    self._child.resizeBy(delta.x(), 0)
                case "Bottom Left":
                    self.setPos(self.pos() + QPointF(delta.x(), 0))
                    self._child.resizeBy(-delta.x(), delta.y())
                case "Bottom Center":
                    self._child.resizeBy(0, delta.y())
                case "Bottom Right":
                    self._child.resizeBy(delta.x(), delta.y())

    def contextMenuEvent(
        self  : Self,
        event : QGraphicsSceneContextMenuEvent
    ) -> None:
        raise NotImplementedError("context menu event not implemented")
