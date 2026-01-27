# unified text item (line or block text)
# parent handles origin, position, rotation
# child handles rotation compensation

from typing import Self

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsItem, QMenu
from PyQt6.QtGui     import QColor, QFont, QAction, QPainterPath

from .....resources.icons import AnchorTopLeftIcon,      \
                                 AnchorTopCenterIcon,    \
                                 AnchorTopRightIcon,     \
                                 AnchorMiddleLeftIcon,   \
                                 AnchorMiddleCenterIcon, \
                                 AnchorMiddleRightIcon,  \
                                 AnchorBottomLeftIcon,   \
                                 AnchorBottomCenterIcon, \
                                 AnchorBottomRightIcon,  \
                                 TextAlignLeftIcon,      \
                                 TextAlignCenterIcon,    \
                                 TextAlignRightIcon,     \
                                 TextAlignTopIcon,       \
                                 TextAlignMiddleIcon,    \
                                 TextAlignBottomIcon

from ...properties import PropertySpec, PropertiesMixin

from .. import Default, DEFAULT, AlignH, AlignV

from ..mixin         import ItemMixin
from ..mixin.origin  import ItemOriginMixin
from ..mixin.pos     import ItemPosMixin
from ..mixin.rotate  import ItemRotateMixin
from ..mixin.paint   import ItemPaintMixin
from ..mixin.handle  import ItemRectHandlesMixin
from ..mixin.quill   import ItemQuillMixin
from ..mixin.outline import ItemOutlineMixin
from ..mixin.change  import ItemChangeMixin
from ..mixin.clone   import ItemCloneMixin
from ..mixin.xml     import ItemXmlMixin
from ..mixin.menu    import ItemMenuMixin

from ..null import NullItem

from .line  import UniTextLineItem
from .block import UniTextBlockItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...views.drawing import DrawingView


class UniTextItem(
    ItemMixin,
    ItemOriginMixin,
    ItemPosMixin,
    ItemRotateMixin,
    ItemPaintMixin,
    ItemRectHandlesMixin,
    ItemQuillMixin,
    ItemOutlineMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemXmlMixin,
    ItemMenuMixin,
    PropertiesMixin,
    NullItem
):
    """
    Text item. Supports line or block text and rotation compensation.
    """

    # class attributes
    _ORIGIN_NAME = "Top Left"
    _RESIZE_KIND = "text"  # handle kind for text items
    _PROPERTIES_ALIGN = \
        {
            "AlignH" : PropertySpec(
                type_name = "AlignH",
                getter    = lambda self: self.horizontalAlignment(),
                setter    = lambda self, value: self.setHorizontalAlignment(value)
            ),
            "AlignV" : PropertySpec(
                type_name = "AlignV",
                valid     = lambda self: self.height() is not None,
                getter    = lambda self: self.verticalAlignment(),
                setter    = lambda self, value: self.setVerticalAlignment(value)
            )
        }
    _PROPERTIES_SIZE = \
        {
            "Width" : PropertySpec(
                type_name = "float",
                valid     = lambda self: self.width() is not None,
                getter    = lambda self: self.width(),
                setter    = lambda self, value: self.setWidth(value)
            ),
            "Height" : PropertySpec(
                type_name = "float",
                valid     = lambda self: self.height() is not None,
                getter    = lambda self: self.height(),
                setter    = lambda self, value: self.setHeight(value)
            )
        }
    _PROPERTIES = \
        {
            "Text" : PropertySpec(
                getter    = lambda self: self.text(),
                setter    = lambda self, value: self.setText(value)
            ),

        } | \
        ItemPosMixin._PROPERTIES_POS | \
        ItemOriginMixin._PROPERTIES_ORIGIN | \
        ItemRotateMixin._PROPERTIES_ROTATE | \
        _PROPERTIES_ALIGN | \
        _PROPERTIES_SIZE | \
        ItemQuillMixin._PROPERTIES_QUILL

    # instance attributes
    _child   : UniTextLineItem | UniTextBlockItem  # text renderer
    _rotcomp : bool                                # rotation compensation
    _align_h : AlignH                              # horizontal alignment
    _align_v : AlignV                              # vertical alignment
    _width   : float | None                        # width constraint
    _height  : float | None                        # height constraint

    def __init__(
        self      : Self,
        pos       : QPointF | None       = None,
        text      : str                  = "",
        block     : bool                 = False,
        rotcomp   : bool                 = True,
        origin    : str                  = "Top Left",
        align_h   : AlignH | None        = None,
        align_v   : AlignV | None        = None,
        width     : float | None         = None,
        height    : float | None         = None,
        color     : QColor | Default     = DEFAULT,
        family    : str    | Default     = DEFAULT,
        size      : float  | Default     = DEFAULT,
        bold      : bool   | Default     = DEFAULT,
        italic    : bool   | Default     = DEFAULT,
        underline : bool   | Default     = DEFAULT,
        parent    : QGraphicsItem | None = None
    ) -> None:
        super().__init__()
        self._child = UniTextBlockItem() if block else UniTextLineItem()
        self._child.setParentItem(self)
        self._child.setText(text)
        self._rotcomp = rotcomp
        self._align_h = align_h or AlignH.LEFT
        self._align_v = align_v or AlignV.TOP
        self._width   = width
        self._height  = height
        self.initItem()
        self.setPos(pos or QPointF(0, 0))
        self.setOrigin(origin)
        if color     : self.setQuillColor(color)
        if family    : self.setQuillFamily(family)
        if size      : self.setQuillSize(size)
        if bold      : self.setQuillBold(bold)
        if italic    : self.setQuillItalic(italic)
        if underline : self.setQuillUnderline(underline)
        self._child.onGeometryChange()
        self.updateHandlePositions()
        self.onSceneRotationChange()

    def onSceneRotationChange(self : Self) -> None:
        if not self._rotcomp:
            return
        a = self.sceneRotation()
        self._child.setRotation(180 if a > 135 and a <= 315 else 0)

    def isSelected(self : Self) -> bool:
        return self._child.isSelected()

    def setSelected(self : Self, selected : bool) -> None:
        self._child.setSelected(selected)

    def block(self : Self) -> bool:
        return isinstance(self._child, UniTextBlockItem)

    def setBlock(self : Self, block : bool) -> None:
        if isinstance(self._child, UniTextLineItem)  and block     \
        or isinstance(self._child, UniTextBlockItem) and not block:
            new_child = UniTextBlockItem() if block else UniTextLineItem()
            new_child.setSelected(self._child.isSelected())
            new_child.setRotation(self._child.rotation())
            new_child.setText(self._child.text())
            new_child.setColor(self._child.color())
            new_child.setFont(self._child.font())
            self._child.setParentItem(None)  # remove old child
            self._child = new_child
            self._child.setParentItem(self)
            self._child.onGeometryChange()
            self.updateHandlePositions()

    def rotcomp(self : Self) -> bool:
        return self._rotcomp

    def setRotcomp(self : Self, rotcomp : bool) -> None:
        self._rotcomp = rotcomp
        if rotcomp:
            self._child.onSceneRotationChange()
        else:
            self._child.setRotation(0)

    def text(self : Self) -> str:
        return self._child.text()

    def setText(self : Self, text : str) -> None:
        self._child.setText(text)
        self._child.onGeometryChange()
        self.updateHandlePositions()
        self.updateProperties("Text")

    def alignH(self : Self) -> AlignH:
        return self._align_h

    def setAlignH(self : Self, align_h : AlignH) -> None:
        self._align_h = align_h
        self._child.onGeometryChange()

    def alignV(self : Self) -> AlignV:
        return self._align_v

    def setAlignV(self : Self, align_v : AlignV) -> None:
        self._align_v = align_v
        self._child.onGeometryChange()

    def width(self : Self) -> float | None:
        return self._width

    def setWidth(self : Self, width : float | None) -> None:
        self._width = width
        if self._child is not None:
            self._child.onGeometryChange()
        self.updateHandlePositions()
        self.updateHandlePaths()
        self.updateProperties(["Width"])

    def height(self : Self) -> float | None:
        return self._height

    def setHeight(self : Self, height : float | None) -> None:
        self._height = height
        if self._child is not None:
            self._child.onGeometryChange()
        self.updateHandlePositions()
        self.updateHandlePaths()
        self.updateProperties(["Height"])

    def color(self : Self) -> QColor:
        return self._child.color()

    def setColor(self : Self, color : QColor) -> None:
        self._child.setColor(color)

    def font(self : Self) -> QFont:
        return self._child.font()

    def setFont(self : Self, font : QFont) -> None:
        self._child.setFont(font)
        self._child.onGeometryChange()
        self.updateHandlePositions()

    def handleRect(self : Self) -> QRectF:
        """Return the rectangle used for handles."""
        return self._child._brect

    def boundingRect(self : Self) -> QRectF:
        """Return the child's bounding rect for hit detection."""
        return self._child._brect

    def shape(self : Self) -> QPainterPath:
        """Return the child's shape for hit detection."""
        return self._child._hshape

    def moveHandleBy(self : Self, name : str, delta : QPointF) -> None:
        """Resize/move the text as appropriate."""
        match name:
            case "Top Left":
                self.moveBy(delta)
                self.resize(-delta.x(), -delta.y())
            case "Top Center":
                self.setY(self.pos().y() + delta.y())
                self.resizeV(-delta.y())
            case "Top Right":
                self.setY(self.pos().y() + delta.y())
                self.resize(delta.x(), -delta.y())
            case "Middle Left":
                self.setX(self.pos().x() + delta.x())
                self.resizeH(-delta.x())
            case "Middle Center":
                self.moveBy(delta)
            case "Middle Right":
                self.resizeH(delta.x())
            case "Bottom Left":
                self.setX(self.pos().x() + delta.x())
                self.resize(-delta.x(), delta.y())
            case "Bottom Center":
                self.resizeV(delta.y())
            case "Bottom Right":
                self.resize(delta.x(), delta.y())

    def resizeH(self : Self, dx : float) -> None:
        rect = self._child._brect
        self._width = max((self._width or rect.width()) + dx, 0.0)
        self._child.onGeometryChange()
        self.updateHandlePositions()
        self.updateHandlePaths()

    def resizeV(self : Self, dy : float) -> None:
        rect = self._child._brect
        self._height = max((self._height or rect.height()) + dy, 0.0)
        self._child.onGeometryChange()
        self.updateHandlePositions()
        self.updateHandlePaths()

    def resize(self : Self, dx : float, dy : float) -> None:
        rect = self._child._brect
        self._width  = max((self._width  or rect.width())  + dx, 0.0)
        self._height = max((self._height or rect.height()) + dy, 0.0)
        self._child.onGeometryChange()
        self.updateHandlePositions()
        self.updateHandlePaths()

    def originMenu(self : Self, view : "DrawingView") -> QMenu:
        menu = QMenu("Origin", view)
        menu.addActions([
            view.action(
                "Top Left",
                lambda: view.ui.editTextBlock(self, anchor="Top Left"),
                checked = self.origin() == "Top Left",
                icon = AnchorTopLeftIcon().get()
            ),
            view.action(
                "Top Center",
                lambda: view.ui.editTextBlock(self, anchor="Top Center"),
                checked = self.origin() == "Top Center",
                icon = AnchorTopCenterIcon().get()
            ),
            view.action(
                "Top Right",
                lambda: view.ui.editTextBlock(self, anchor="Top Right"),
                checked = self.origin() == "Top Right",
                icon = AnchorTopRightIcon().get()
            ),
            view.action(
                "Middle Left",
                lambda: view.ui.editTextBlock(self, anchor="Middle Left"),
                checked = self.origin() == "Middle Left",
                icon = AnchorMiddleLeftIcon().get()
            ),
            view.action(
                "Middle Center",
                lambda: view.ui.editTextBlock(self, anchor="Middle Center"),
                checked = self.origin() == "Middle Center",
                icon = AnchorMiddleCenterIcon().get()
            ),
            view.action(
                "Middle Right",
                lambda: view.ui.editTextBlock(self, anchor="Middle Right"),
                checked = self.origin() == "Middle Right",
                icon = AnchorMiddleRightIcon().get()
            ),
            view.action(
                "Bottom Left",
                lambda: view.ui.editTextBlock(self, anchor="Bottom Left"),
                checked = self.origin() == "Bottom Left",
                icon = AnchorBottomLeftIcon().get()
            ),
            view.action(
                "Bottom Center",
                lambda: view.ui.editTextBlock(self, anchor="Bottom Center"),
                checked = self.origin() == "Bottom Center",
                icon = AnchorBottomCenterIcon().get()
            ),
            view.action(
                "Bottom Right",
                lambda: view.ui.editTextBlock(self, anchor="Bottom Right"),
                checked = self.origin() == "Bottom Right",
                icon = AnchorBottomRightIcon().get()
            )
        ])
        return menu

    def alignmentMenu(self : Self, view : "DrawingView") -> QMenu:
        menu = QMenu("Alignment", view)
        menu.addActions([
            view.action(
                "Left",
                lambda: view.ui.editText(self, align_h=AlignH.LEFT),
                checked = self.alignH() == AlignH.LEFT,
                icon = TextAlignLeftIcon().get()
            ),
            view.action(
                "Center",
                lambda: view.ui.editText(self, align_h=AlignH.CENTER),
                    checked = self.alignH() == AlignH.CENTER,
                icon = TextAlignCenterIcon().get()
            ),
            view.action(
                "Right",
                lambda: view.ui.editText(self, align_h=AlignH.RIGHT),
                checked = self.alignH() == AlignH.RIGHT,
                icon = TextAlignRightIcon().get()
            ),
            view.separator(),
            view.action(
                "Top",
                lambda: view.ui.editText(self, align_v=AlignV.TOP),
                checked = self.alignV() == AlignV.TOP,
                icon = TextAlignTopIcon().get(),
                enabled = self.height() is not None
            ),
            view.action(
                "Middle",
                lambda: view.ui.editText(self, align_v=AlignV.MIDDLE),
                checked = self.alignV() == AlignV.MIDDLE,
                icon = TextAlignMiddleIcon().get(),
                enabled = self.height() is not None
            ),
            view.action(
                "Bottom",
                lambda: view.ui.editText(self, align_v=AlignV.BOTTOM),
                checked = self.alignV() == AlignV.BOTTOM,
                icon = TextAlignBottomIcon().get(),
                enabled = self.height() is not None
            )
        ])
        return menu

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        """Return context menu items for UniText item."""
        items = [
            view.action("Edit...", view.ui.editTextDialog),
            view.separator(),
            self.originMenu(view),
            self.alignmentMenu(view),
            view.separator(),
            view.action(
                "Auto Width", lambda: self.setWidth(
                    self.boundingRect().width() if self._width is None else None
                ),
                self._width is None
            ),
            view.action(
                "Auto Height", lambda: self.setHeight(
                    self.boundingRect().height() if self._height is None else None
                ),
                self._height is None
            ),
            view.separator(),
            view.action("Properties...", lambda: view.ui.editItemProperties(self))
        ]
        return items
