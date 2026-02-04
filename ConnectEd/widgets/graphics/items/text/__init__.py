# unified text item (line or block text)
# parent handles origin, position, rotation
# child handles rotation compensation

from typing      import Self
from dataclasses import dataclass

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

from ...properties import InherentProperty, PropertiesMixin

from .. import Default, DEFAULT, NoChange, NO_CHANGE, AlignH, AlignV

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

from .line  import TextLineRenderer
from .block import TextBlockRenderer

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...views.drawing import DrawingView


@dataclass
class TextState:
    text      : str
    block     : bool
    rotcomp   : bool
    origin    : str
    align_h   : AlignH
    align_v   : AlignV
    width     : float
    height    : float
    color     : QColor | Default
    family    : str    | Default
    size      : float  | Default
    bold      : bool   | Default
    italic    : bool   | Default
    underline : bool   | Default

    @classmethod
    def fromItem(cls, item : "TextItem") -> Self:
        return cls(
            text      = item.text(),
            block     = item.block(),
            rotcomp   = item.rotcomp(),
            origin    = item.origin(),
            align_h   = item.alignH(),
            align_v   = item.alignV(),
            width     = item.width(),
            height    = item.height(),
            color     = item.quillColor(),
            family    = item.quillFamily(),
            size      = item.quillSize(),
            bold      = item.quillBold(),
            italic    = item.quillItalic(),
            underline = item.quillUnderline()
        )


@dataclass
class TextChange:
    text      : str              | NoChange = NO_CHANGE
    block     : bool             | NoChange = NO_CHANGE
    rotcomp   : bool             | NoChange = NO_CHANGE
    origin    : str              | NoChange = NO_CHANGE
    align_h   : AlignH           | NoChange = NO_CHANGE
    align_v   : AlignV           | NoChange = NO_CHANGE
    width     : float            | NoChange = NO_CHANGE
    height    : float            | NoChange = NO_CHANGE
    color     : QColor | Default | NoChange = NO_CHANGE
    family    : str    | Default | NoChange = NO_CHANGE
    size      : float  | Default | NoChange = NO_CHANGE
    bold      : bool   | Default | NoChange = NO_CHANGE
    italic    : bool   | Default | NoChange = NO_CHANGE
    underline : bool   | Default | NoChange = NO_CHANGE


class TextItem(
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
            "AlignH" : InherentProperty(
                type_name = "AlignH",
                getter    = lambda self: self.horizontalAlignment(),
                setter    = lambda self, value: self.setHorizontalAlignment(value)
            ),
            "AlignV" : InherentProperty(
                type_name = "AlignV",
                valid     = lambda self: self.height() >= 0.0,
                getter    = lambda self: self.verticalAlignment(),
                setter    = lambda self, value: self.setVerticalAlignment(value)
            )
        }
    _PROPERTIES_SIZE = \
        {
            "Width" : InherentProperty(
                type_name = "float",
                valid     = lambda self: self.width() >= 0.0,
                getter    = lambda self: self.width(),
                setter    = lambda self, value: self.setWidth(value)
            ),
            "Height" : InherentProperty(
                type_name = "float",
                valid     = lambda self: self.height() >= 0.0,
                getter    = lambda self: self.height(),
                setter    = lambda self, value: self.setHeight(value)
            )
        }
    _PROPERTIES = \
        {
            "Text" : InherentProperty(
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
    _child   : TextLineRenderer | TextBlockRenderer  # text renderer
    _rotcomp : bool                                  # rotation compensation
    _align_h : AlignH                                # horizontal alignment
    _align_v : AlignV                                # vertical alignment
    _width   : float                                 # width constraint
    _height  : float                                 # height constraint

    def __init__(
        self      : Self,
        text      : str                  = "",
        block     : bool                 = False,
        rotcomp   : bool                 = True,
        pos       : QPointF | None       = None,
        origin    : str                  = "Top Left",
        align_h   : AlignH               = AlignH.LEFT,
        align_v   : AlignV               = AlignV.TOP,
        width     : float                = -1.0,        # unconstrained
        height    : float                = -1.0,        # unconstrained
        color     : QColor | Default     = DEFAULT,
        family    : str    | Default     = DEFAULT,
        size      : float  | Default     = DEFAULT,
        bold      : bool   | Default     = DEFAULT,
        italic    : bool   | Default     = DEFAULT,
        underline : bool   | Default     = DEFAULT,
        fresh     : bool                 = True,
        parent    : QGraphicsItem | None = None
    ) -> None:
        super().__init__()
        self._child = TextBlockRenderer() if block else TextLineRenderer()
        self._child.setParentItem(self)
        self._child.setText(text)
        self._rotcomp = rotcomp
        self._align_h = align_h
        self._align_v = align_v
        self._width   = width
        self._height  = height
        self.initItem(fresh)
        self.setPos(pos or QPointF(0, 0))
        self.setOrigin(origin)
        self.setQuillColor(color)
        self.setQuillFamily(family)
        self.setQuillSize(size)
        self.setQuillBold(bold)
        self.setQuillItalic(italic)
        self.setQuillUnderline(underline)
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
        return isinstance(self._child, TextBlockRenderer)

    def setBlock(self : Self, block : bool) -> None:
        if isinstance(self._child, TextLineRenderer)  and block     \
        or isinstance(self._child, TextBlockRenderer) and not block:
            new_child = TextBlockRenderer() if block else TextLineRenderer()
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
            self.onSceneRotationChange()
        else:
            self._child.setRotation(0)

    def text(self : Self) -> str:
        return self._child.text()

    def setText(self : Self, text : str) -> None:
        self._child.setText(text)
        self._child.onGeometryChange()
        self.updateHandlePositions()
        self.signalPropertyChanges("Text")

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

    def width(self : Self) -> float:
        return self._width

    def setWidth(self : Self, width : float) -> None:
        self._width = width
        if self._child is not None:
            self._child.onGeometryChange()
        self.updateHandlePositions()
        self.updateHandlePaths()
        self.signalPropertyChanges("Width")

    def height(self : Self) -> float:
        return self._height

    def setHeight(self : Self, height : float) -> None:
        self._height = height
        if self._child is not None:
            self._child.onGeometryChange()
        self.updateHandlePositions()
        self.updateHandlePaths()
        self.signalPropertyChanges("Height")

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
        origin = self.origin()
        match name:
            case "Top Left":
                if "Left" in origin: self.moveByX(delta.x())
                self.resizeX(-delta.x())
                if "Top" in origin: self.moveByY(delta.y())
                self.resizeY(-delta.y())
            case "Top Center":
                if "Top" in origin: self.moveByY(delta.y())
                self.resizeY(-delta.y())
            case "Top Right":
                if "Right" in origin: self.moveByX(delta.x())
                self.resizeX(delta.x())
                if "Top" in origin: self.moveByY(delta.y())
                self.resizeY(-delta.y())
            case "Middle Left":
                if "Left" in origin: self.moveByX(delta.x())
                self.resizeX(-delta.x())
            case "Middle Center":
                self.moveBy(delta)
            case "Middle Right":
                if "Right" in origin: self.moveByX(delta.x())
                self.resizeX(delta.x())
            case "Bottom Left":
                if "Left" in origin: self.moveByX(delta.x())
                self.resizeX(-delta.x())
                if "Bottom" in origin: self.moveByY(delta.y())
                self.resizeY(delta.y())
            case "Bottom Center":
                if "Bottom" in origin: self.moveByY(delta.y())
                self.resizeY(delta.y())
            case "Bottom Right":
                if "Right" in origin: self.moveByX(delta.x())
                self.resizeX(delta.x())
                if "Bottom" in origin: self.moveByY(delta.y())
                self.resizeY(delta.y())

    def moveByX(self : Self, dx : float) -> None:
        self.setX(self.pos().x() + dx)

    def moveByY(self : Self, dy : float) -> None:
        self.setY(self.pos().y() + dy)

    def resizeX(self : Self, dx : float) -> None:
        rect = self._child._brect
        width = self._width if self._width >= 0.0 else rect.width()
        self._width = max(width + dx, 0.0)
        self._child.onGeometryChange()
        self.updateHandlePositions()
        self.updateHandlePaths()

    def resizeY(self : Self, dy : float) -> None:
        rect = self._child._brect
        height = self._height if self._height >= 0.0 else rect.height()
        self._height = max(height + dy, 0.0)
        self._child.onGeometryChange()
        self.updateHandlePositions()
        self.updateHandlePaths()

    def resize(self : Self, dx : float, dy : float) -> None:
        rect = self._child._brect
        width = self._width if self._width >= 0.0 else rect.width()
        height = self._height if self._height >= 0.0 else rect.height()
        self._width  = max(width  + dx, 0.0)
        self._height = max(height + dy, 0.0)
        self._child.onGeometryChange()
        self.updateHandlePositions()
        self.updateHandlePaths()

    def originMenu(self : Self, view : "DrawingView") -> QMenu:
        menu = QMenu("Origin", view)
        menu.addActions([
            view.action(
                "Top Left",
                lambda: view.ui.editText(self, origin="Top Left"),
                checked = self.origin() == "Top Left",
                icon = AnchorTopLeftIcon().get()
            ),
            view.action(
                "Top Center",
                lambda: view.ui.editText(self, origin="Top Center"),
                checked = self.origin() == "Top Center",
                icon = AnchorTopCenterIcon().get()
            ),
            view.action(
                "Top Right",
                lambda: view.ui.editText(self, origin="Top Right"),
                checked = self.origin() == "Top Right",
                icon = AnchorTopRightIcon().get()
            ),
            view.action(
                "Middle Left",
                lambda: view.ui.editText(self, origin="Middle Left"),
                checked = self.origin() == "Middle Left",
                icon = AnchorMiddleLeftIcon().get()
            ),
            view.action(
                "Middle Center",
                lambda: view.ui.editText(self, origin="Middle Center"),
                checked = self.origin() == "Middle Center",
                icon = AnchorMiddleCenterIcon().get()
            ),
            view.action(
                "Middle Right",
                lambda: view.ui.editText(self, origin="Middle Right"),
                checked = self.origin() == "Middle Right",
                icon = AnchorMiddleRightIcon().get()
            ),
            view.action(
                "Bottom Left",
                lambda: view.ui.editText(self, origin="Bottom Left"),
                checked = self.origin() == "Bottom Left",
                icon = AnchorBottomLeftIcon().get()
            ),
            view.action(
                "Bottom Center",
                lambda: view.ui.editText(self, origin="Bottom Center"),
                checked = self.origin() == "Bottom Center",
                icon = AnchorBottomCenterIcon().get()
            ),
            view.action(
                "Bottom Right",
                lambda: view.ui.editText(self, origin="Bottom Right"),
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
                enabled = self.height() >= 0.0
            ),
            view.action(
                "Middle",
                lambda: view.ui.editText(self, align_v=AlignV.MIDDLE),
                checked = self.alignV() == AlignV.MIDDLE,
                icon = TextAlignMiddleIcon().get(),
                enabled = self.height() >= 0.0
            ),
            view.action(
                "Bottom",
                lambda: view.ui.editText(self, align_v=AlignV.BOTTOM),
                checked = self.alignV() == AlignV.BOTTOM,
                icon = TextAlignBottomIcon().get(),
                enabled = self.height() >= 0.0
            )
        ])
        return menu

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        """Return context menu items for Text item."""
        items = [
            view.action("Edit...", view.ui.editTextDialog),
            view.separator(),
            self.originMenu(view),
            self.alignmentMenu(view),
            view.separator(),
            view.action(
                "Auto Width", lambda: self.setWidth(
                    self.boundingRect().width() if self._width < 0.0 else -1.0
                ),
                self._width < 0.0
            ),
            view.action(
                "Auto Height", lambda: self.setHeight(
                    self.boundingRect().height() if self._height < 0.0 else -1.0
                ),
                self._height < 0.0
            ),
            view.separator(),
            view.action("Properties...", lambda: view.ui.editItemProperties(self))
        ]
        return items
