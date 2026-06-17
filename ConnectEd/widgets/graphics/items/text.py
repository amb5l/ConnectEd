from typing      import Self, Any
from dataclasses import dataclass

from PyQt6.QtCore    import Qt, QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsItem, QMenu, \
                            QStyleOptionGraphicsItem, QStyle, QWidget, \
                            QGraphicsSceneContextMenuEvent, \
                            QGraphicsSimpleTextItem, QGraphicsTextItem
from PyQt6.QtGui     import QColor, QFont, QAction, QPainter, QPainterPath, \
                            QTransform, QTextCursor

from ....core.types import NoChange, NO_CHANGE, \
                           AlignH, AlignV, RectHandleId, DataKind

from ....resources.icons import AnchorTopLeftIcon,      \
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

from ....core.check import checked

from ..properties import InherentProperty
from ..quill      import Quill

from .grip import ResizeGripItem

from .role import DecorativeItem

from .mixin              import PrimaryItemMixin
from .mixin.transform    import ItemTransformMixin
from .mixin.handle       import ItemRectHandlesMixin
from .mixin.shape        import ItemShapeMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing  import DrawingView
    from ...dialogs.items.text import BaseTextItemDialog, TextItemDialog


@dataclass
class TextState:
    text       : str
    block      : bool
    rotation   : float
    mirror_h   : bool
    mirror_v   : bool
    autoflip   : bool
    origin     : RectHandleId
    align_h    : AlignH
    align_v    : AlignV
    width      : float
    height     : float
    pad_left   : float
    pad_right  : float
    pad_top    : float
    pad_bottom : float
    color      : QColor | None
    font       : str    | None
    size       : float  | None
    bold       : bool   | None
    italic     : bool   | None
    underline  : bool   | None

    @classmethod
    def fromItem(cls, item : "TextItem") -> Self:
        return cls(
            text       = item.text(),
            block      = item.block(),
            rotation   = item.rotation(),
            mirror_h   = item.mirrorH(),
            mirror_v   = item.mirrorV(),
            autoflip   = item.autoflip(),
            origin     = item.origin(),
            align_h    = item.alignH(),
            align_v    = item.alignV(),
            width      = item.width(),
            height     = item.height(),
            pad_left   = item.padLeft(),
            pad_right  = item.padRight(),
            pad_top    = item.padTop(),
            pad_bottom = item.padBottom(),
            color      = item.textColor(),
            font       = item.textFont(),
            size       = item.textSize(),
            bold       = item.textBold(),
            italic     = item.textItalic(),
            underline  = item.textUnderline()
        )


@dataclass
class TextChange:
    text       : str           | NoChange = NO_CHANGE
    block      : bool          | NoChange = NO_CHANGE
    rotation   : float         | NoChange = NO_CHANGE
    mirror_h   : bool          | NoChange = NO_CHANGE
    mirror_v   : bool          | NoChange = NO_CHANGE
    autoflip   : bool          | NoChange = NO_CHANGE
    origin     : str           | NoChange = NO_CHANGE
    align_h    : AlignH        | NoChange = NO_CHANGE
    align_v    : AlignV        | NoChange = NO_CHANGE
    width      : float         | NoChange = NO_CHANGE
    height     : float         | NoChange = NO_CHANGE
    pad_left   : float         | NoChange = NO_CHANGE
    pad_right  : float         | NoChange = NO_CHANGE
    pad_top    : float         | NoChange = NO_CHANGE
    pad_bottom : float         | NoChange = NO_CHANGE
    color      : QColor | None | NoChange = NO_CHANGE
    font       : str    | None | NoChange = NO_CHANGE
    size       : float  | None | NoChange = NO_CHANGE
    bold       : bool   | None | NoChange = NO_CHANGE
    italic     : bool   | None | NoChange = NO_CHANGE
    underline  : bool   | None | NoChange = NO_CHANGE


class TextResizeGripItem(ResizeGripItem):
    """Grip for resizing text items."""

    @checked
    def moveSave(self : Self) -> tuple[QPointF, float | None, float | None]:
        item : "TextItem" = self.item()
        return self.scenePos(), item.width(), item.height()

    @checked
    def moveRestore(
        self  : Self,
        state : tuple[QPointF, float | None, float | None]
    ) -> None:
        pos, width, height = state
        item : "TextItem" = self.item()
        self.moveBy(pos - self.scenePos())
        item.setWidth(width)
        item.setHeight(height)


class BaseTextItem(
    ItemTransformMixin,
    ItemRectHandlesMixin,
    ItemShapeMixin,
    PrimaryItemMixin,
    QGraphicsItem
):
    """
    Text item. Supports line or block text and rotation compensation.
    """

    # class attributes
    _ORIGIN = RectHandleId.TOP_LEFT
    _RESIZE_GRIP_CLS = TextResizeGripItem
    _PROPERTIES_ALIGN = \
        {
            "AlignH" : InherentProperty(
                kind   = DataKind.ALIGN_H,
                getter = lambda self: self.alignH(),
                setter = lambda self, value: self.setAlignH(value)
            ),
            "AlignV" : InherentProperty(
                kind   = DataKind.ALIGN_V,
                getter = lambda self: self.alignV(),
                setter = lambda self, value: self.setAlignV(value)
            )
        }
    _PROPERTIES_SIZE = \
        {
            "Width" : InherentProperty(
                kind   = DataKind.SIZE,
                worthy = lambda self: self.width() >= 0.0,
                getter = lambda self: self.width(),
                setter = lambda self, value: self.setWidth(value)
            ),
            "Height" : InherentProperty(
                kind   = DataKind.SIZE,
                worthy = lambda self: self.height() >= 0.0,
                getter = lambda self: self.height(),
                setter = lambda self, value: self.setHeight(value)
            )
        }
    _PROPERTIES_PADDING = \
        {
            "Pad Left" : InherentProperty(
                kind   = DataKind.FLOAT,
                worthy = lambda self: self.padLeft() != 0.0,
                getter = lambda self: self.padLeft(),
                setter = lambda self, value: self.setPadLeft(value)
            ),
            "Pad Right" : InherentProperty(
                kind   = DataKind.FLOAT,
                worthy = lambda self: self.padRight() != 0.0,
                getter = lambda self: self.padRight(),
                setter = lambda self, value: self.setPadRight(value)
            ),
            "Pad Top" : InherentProperty(
                kind   = DataKind.FLOAT,
                worthy = lambda self: self.padTop() != 0.0,
                getter = lambda self: self.padTop(),
                setter = lambda self, value: self.setPadTop(value)
            ),
            "Pad Bottom" : InherentProperty(
                kind   = DataKind.FLOAT,
                worthy = lambda self: self.padBottom() != 0.0,
                getter = lambda self: self.padBottom(),
                setter = lambda self, value: self.setPadBottom(value)
            )
        }
    _PROPERTIES = \
        {
            "Text" : InherentProperty(
                kind   = DataKind.STR,
                getter = lambda self: self.text(),
                setter = lambda self, value: self.setText(value)
            ),
            "Block" : InherentProperty(
                kind   = DataKind.BOOL,
                worthy = lambda self: self.block(),
                getter = lambda self: self.block(),
                setter = lambda self, value: self.setBlock(value)
            ),
            "AutoFlip" : InherentProperty(
                kind   = DataKind.BOOL,
                worthy = lambda self: not self.autoflip(),
                getter = lambda self: self.autoflip(),
                setter = lambda self, value: self.setAutoflip(value)
            )
        } | \
        ItemTransformMixin._PROPERTIES_POS         | \
        ItemTransformMixin._PROPERTIES_ROTATE      | \
        ItemTransformMixin._PROPERTIES_MIRROR      | \
        ItemTransformMixin._PROPERTIES_RECT_ORIGIN | \
        _PROPERTIES_ALIGN                          | \
        _PROPERTIES_SIZE                           | \
        _PROPERTIES_PADDING                        | \
        PrimaryItemMixin._PROPERTIES_TEXT

    # instance attributes
    _child      : "TextLineRenderer | TextBlockRenderer"  # text renderer
    _autoflip   : bool                                    # orientation compensation
    _align_h    : AlignH                                  # horizontal alignment
    _align_v    : AlignV                                  # vertical alignment
    _width      : float                                   # width constraint
    _height     : float                                   # height constraint
    _pad_left   : float                                   # left padding
    _pad_right  : float                                   # right padding
    _pad_top    : float                                   # top padding
    _pad_bottom : float                                   # bottom padding
    _brect      : QRectF                                  # bounding rect

    _text_color     = None  # enable per-item appearance control
    _text_font      = None  # enable per-item appearance control
    _text_size      = None  # enable per-item appearance control
    _text_bold      = None  # enable per-item appearance control
    _text_italic    = None  # enable per-item appearance control
    _text_underline = None  # enable per-item appearance control

    @checked
    def __init__(
        self       : Self,
        text       : str                  = "",
        block      : bool                 = False,
        pos        : QPointF       | None = None,
        rotation   : float                = 0.0,
        mirror_h   : bool                 = False,
        mirror_v   : bool                 = False,
        autoflip   : bool                 = True,
        origin     : RectHandleId         = RectHandleId.TOP_LEFT,
        align_h    : AlignH               = AlignH.LEFT,
        align_v    : AlignV               = AlignV.TOP,
        width      : float                = -1.0,        # unconstrained
        height     : float                = -1.0,        # unconstrained
        pad_left   : float                = 0.0,
        pad_right  : float                = 0.0,
        pad_top    : float                = 0.0,
        pad_bottom : float                = 0.0,
        color      : QColor        | None = None,
        font       : str           | None = None,
        size       : float         | None = None,
        bold       : bool          | None = None,
        italic     : bool          | None = None,
        underline  : bool          | None = None,
        fresh      : bool                 = True,
        parent     : QGraphicsItem | None = None
    ) -> None:
        super().__init__(parent)
        self._autoflip   = autoflip
        self._align_h    = align_h
        self._align_v    = align_v
        self._width      = width
        self._height     = height
        self._pad_left   = pad_left
        self._pad_right  = pad_right
        self._pad_top    = pad_top
        self._pad_bottom = pad_bottom
        self._hshape = QPainterPath()
        self._child = TextBlockRenderer() if block else TextLineRenderer()
        self._child.setParentItem(self)
        self._child._setText(text)
        self.initItem(fresh)
        self.setFlag(self.GraphicsItemFlag.ItemHasNoContents, True)
        self.setPos(pos or QPointF(0, 0))
        self.setRotation(rotation)
        self.setMirrorH(mirror_h)
        self.setMirrorV(mirror_v)
        self.setOrigin(origin)
        self.setTextColor(color)
        self.setTextFont(font)
        self.setTextSize(size)
        self.setTextBold(bold)
        self.setTextItalic(italic)
        self.setTextUnderline(underline)
        self.onGeometryChanged()

    def onGeometryChanged(self : Self) -> None:
        """Re-layout rendered text and sync handles."""
        self._child.onGeometryChanged()
        self.updateHandlePositions()

    def onSceneRotationChanged(self : Self) -> None:
        self._child.onSceneOrientationChanged()

    def onSceneMirrorChanged(self : Self) -> None:
        self._child.onSceneOrientationChanged()

    def onOriginChanged(
        self : Self,
        _old : RectHandleId | None,
        _new : RectHandleId,
    ) -> None:
        self.onGeometryChanged()

    def block(self : Self) -> bool:
        return isinstance(self._child, TextBlockRenderer)

    @checked
    def setBlock(self : Self, block : bool) -> None:
        if isinstance(self._child, TextLineRenderer)  and block     \
        or isinstance(self._child, TextBlockRenderer) and not block:
            new_child = TextBlockRenderer() if block else TextLineRenderer()
            new_child.setRotation(self._child.rotation())
            new_child.setText(self._child.text())
            new_child.setColor(self._child.color())
            new_child.setFont(self._child.font())
            self._child.setParentItem(None)  # remove old child
            self._child = new_child
            self._child.setParentItem(self)
            self.onGeometryChanged()
            # subclasses may not expose the block property:
            if self.properties.has("Block"):
                self.properties.signalChanges("Block")

    def autoflip(self : Self) -> bool:
        return self._autoflip

    @checked
    def setAutoflip(self : Self, autoflip : bool) -> None:
        self._autoflip = autoflip
        self._child.onSceneOrientationChanged()
        self.properties.signalChanges("AutoFlip")

    def text(self : Self) -> str:
        return self._child.text()

    @checked
    def setText(self : Self, text : str) -> None:
        self._child._setText(text)
        self.onGeometryChanged()
        self.properties.signalChanges("Text")

    def alignH(self : Self) -> AlignH:
        return self._align_h

    @checked
    def setAlignH(self : Self, align_h : AlignH) -> None:
        self._align_h = align_h
        self._child.onGeometryChanged()
        self.properties.signalChanges("AlignH")

    def alignV(self : Self) -> AlignV:
        return self._align_v

    @checked
    def setAlignV(self : Self, align_v : AlignV) -> None:
        self._align_v = align_v
        self._child.onGeometryChanged()
        self.properties.signalChanges("AlignV")

    def width(self : Self) -> float:
        return self._width

    @checked
    def setWidth(self : Self, width : float) -> None:
        self._width = width
        self.onGeometryChanged()
        self.properties.signalChanges("Width")

    def height(self : Self) -> float:
        return self._height

    @checked
    def setHeight(self : Self, height : float) -> None:
        self._height = height
        self.onGeometryChanged()
        self.properties.signalChanges("Height")

    def padLeft(self : Self) -> float:
        return self._pad_left

    @checked
    def setPadLeft(self : Self, pad_left : float) -> None:
        self._pad_left = max(pad_left, 0.0)
        self.onGeometryChanged()
        self.properties.signalChanges("Pad Left")

    def padRight(self : Self) -> float:
        return self._pad_right

    @checked
    def setPadRight(self : Self, pad_right : float) -> None:
        self._pad_right = max(pad_right, 0.0)
        self.onGeometryChanged()
        self.properties.signalChanges("Pad Right")

    def padTop(self : Self) -> float:
        return self._pad_top

    @checked
    def setPadTop(self : Self, pad_top : float) -> None:
        self._pad_top = max(pad_top, 0.0)
        self.onGeometryChanged()
        self.properties.signalChanges("Pad Top")

    def padBottom(self : Self) -> float:
        return self._pad_bottom

    @checked
    def setPadBottom(self : Self, pad_bottom : float) -> None:
        self._pad_bottom = max(pad_bottom, 0.0)
        self.onGeometryChanged()
        self.properties.signalChanges("Pad Bottom")

    def color(self : Self) -> QColor:
        return self._child.color()

    @checked
    def setColor(self : Self, color : QColor) -> None:
        self._child.setColor(color)

    def font(self : Self) -> QFont:
        return self._child.font()

    @checked
    def setFont(self : Self, font : QFont) -> None:
        self._child.setFont(font)
        self.onGeometryChanged()

    def quill(self : Self) -> Quill:
        qfont = self.font()
        return Quill(
            self.color(),
            qfont.family(),
            qfont.pointSizeF(),
            qfont.bold(),
            qfont.italic(),
            qfont.underline()
        )

    @checked
    def setQuill(self : Self, quill : Quill) -> None:
        self.setColor(quill.color())
        self.setFont(quill.qFont())

    def handleRect(self : Self) -> QRectF:
        """Return the rectangle used for handles."""
        return self._brect

    @checked
    def moveHandleBy(self : Self, id : RectHandleId, delta : QPointF) -> None:
        """
        Resize/move the text as appropriate. `delta` is supplied in scene
        coordinates; convert it to a parent-local delta (for repositioning
        self, whose pos() lives in parent coordinates) and an item-local
        delta (for width/height, which live in the item's own frame) so
        that any mirror or rotation of self/parent is respected.
        """
        zero = QPointF(0, 0)
        parent = self.parentItem()
        if parent is None:
            pd = delta
        else:
            pd = parent.mapFromScene(delta) - parent.mapFromScene(zero)
        ld = self.mapFromScene(delta) - self.mapFromScene(zero)
        origin_name = self.origin().value
        match id:
            case RectHandleId.TOP_LEFT:
                if "Left" in origin_name: self.moveByX(pd.x())
                self.resizeX(-ld.x())
                if "Top" in origin_name: self.moveByY(pd.y())
                self.resizeY(-ld.y())
            case RectHandleId.TOP_CENTER:
                if "Top" in origin_name: self.moveByY(pd.y())
                self.resizeY(-ld.y())
            case RectHandleId.TOP_RIGHT:
                if "Right" in origin_name: self.moveByX(pd.x())
                self.resizeX(ld.x())
                if "Top" in origin_name: self.moveByY(pd.y())
                self.resizeY(-ld.y())
            case RectHandleId.MIDDLE_LEFT:
                if "Left" in origin_name: self.moveByX(pd.x())
                self.resizeX(-ld.x())
            case RectHandleId.MIDDLE_CENTER:
                self.moveBy(pd)
            case RectHandleId.MIDDLE_RIGHT:
                if "Right" in origin_name: self.moveByX(pd.x())
                self.resizeX(ld.x())
            case RectHandleId.BOTTOM_LEFT:
                if "Left" in origin_name: self.moveByX(pd.x())
                self.resizeX(-ld.x())
                if "Bottom" in origin_name: self.moveByY(pd.y())
                self.resizeY(ld.y())
            case RectHandleId.BOTTOM_CENTER:
                if "Bottom" in origin_name: self.moveByY(pd.y())
                self.resizeY(ld.y())
            case RectHandleId.BOTTOM_RIGHT:
                if "Right" in origin_name: self.moveByX(pd.x())
                self.resizeX(ld.x())
                if "Bottom" in origin_name: self.moveByY(pd.y())
                self.resizeY(ld.y())

    def moveByX(self : Self, dx : float) -> None:
        self.setX(self.pos().x() + dx)

    def moveByY(self : Self, dy : float) -> None:
        self.setY(self.pos().y() + dy)

    def resizeX(self : Self, dx : float) -> None:
        rect = self._brect
        width = self._width if self._width >= 0.0 else rect.width()
        self._width = max(width + dx, 0.0)
        self.onGeometryChanged()

    def resizeY(self : Self, dy : float) -> None:
        rect = self._brect
        height = self._height if self._height >= 0.0 else rect.height()
        self._height = max(height + dy, 0.0)
        self.onGeometryChanged()

    def resize(self : Self, dx : float, dy : float) -> None:
        rect = self._brect
        width = self._width if self._width >= 0.0 else rect.width()
        height = self._height if self._height >= 0.0 else rect.height()
        self._width  = max(width  + dx, 0.0)
        self._height = max(height + dy, 0.0)
        self.onGeometryChanged()

    def boundingRect(self : Self) -> QRectF:
        return self._brect

    def originMenu(self : Self, view : "DrawingView") -> QMenu:
        menu = QMenu("Origin", view)
        menu.addActions([
            view.action(
                "Top Left",
                lambda: view.editText(self, origin="Top Left"),
                checked = self.origin() == "Top Left",
                icon = AnchorTopLeftIcon().get()
            ),
            view.action(
                "Top Center",
                lambda: view.editText(self, origin="Top Center"),
                checked = self.origin() == "Top Center",
                icon = AnchorTopCenterIcon().get()
            ),
            view.action(
                "Top Right",
                lambda: view.editText(self, origin="Top Right"),
                checked = self.origin() == "Top Right",
                icon = AnchorTopRightIcon().get()
            ),
            view.action(
                "Middle Left",
                lambda: view.editText(self, origin="Middle Left"),
                checked = self.origin() == "Middle Left",
                icon = AnchorMiddleLeftIcon().get()
            ),
            view.action(
                "Middle Center",
                lambda: view.editText(self, origin="Middle Center"),
                checked = self.origin() == "Middle Center",
                icon = AnchorMiddleCenterIcon().get()
            ),
            view.action(
                "Middle Right",
                lambda: view.editText(self, origin="Middle Right"),
                checked = self.origin() == "Middle Right",
                icon = AnchorMiddleRightIcon().get()
            ),
            view.action(
                "Bottom Left",
                lambda: view.editText(self, origin="Bottom Left"),
                checked = self.origin() == "Bottom Left",
                icon = AnchorBottomLeftIcon().get()
            ),
            view.action(
                "Bottom Center",
                lambda: view.editText(self, origin="Bottom Center"),
                checked = self.origin() == "Bottom Center",
                icon = AnchorBottomCenterIcon().get()
            ),
            view.action(
                "Bottom Right",
                lambda: view.editText(self, origin="Bottom Right"),
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
                lambda: view.editText(self, align_h=AlignH.LEFT),
                checked = self.alignH() == AlignH.LEFT,
                icon = TextAlignLeftIcon().get()
            ),
            view.action(
                "Center",
                lambda: view.editText(self, align_h=AlignH.CENTER),
                    checked = self.alignH() == AlignH.CENTER,
                icon = TextAlignCenterIcon().get()
            ),
            view.action(
                "Right",
                lambda: view.editText(self, align_h=AlignH.RIGHT),
                checked = self.alignH() == AlignH.RIGHT,
                icon = TextAlignRightIcon().get()
            ),
            view.separator(),
            view.action(
                "Top",
                lambda: view.editText(self, align_v=AlignV.TOP),
                checked = self.alignV() == AlignV.TOP,
                icon = TextAlignTopIcon().get(),
                enabled = self.height() >= 0.0
            ),
            view.action(
                "Middle",
                lambda: view.editText(self, align_v=AlignV.MIDDLE),
                checked = self.alignV() == AlignV.MIDDLE,
                icon = TextAlignMiddleIcon().get(),
                enabled = self.height() >= 0.0
            ),
            view.action(
                "Bottom",
                lambda: view.editText(self, align_v=AlignV.BOTTOM),
                checked = self.alignV() == AlignV.BOTTOM,
                icon = TextAlignBottomIcon().get(),
                enabled = self.height() >= 0.0
            )
        ])
        return menu

    @checked
    def _applyDialogCommon(self : Self, dialog : "BaseTextItemDialog") -> None:
        rotation   = dialog.getRotation()
        autoflip   = dialog.getAutoflip()
        mirror_h   = dialog.getMirrorH()
        mirror_v   = dialog.getMirrorV()
        align_h    = dialog.getAlignH()
        align_v    = dialog.getAlignV()
        origin     = dialog.getOrigin()
        pad_left   = dialog.getPadLeft()
        pad_right  = dialog.getPadRight()
        pad_top    = dialog.getPadTop()
        pad_bottom = dialog.getPadBottom()
        color      = dialog.getColor()
        font       = dialog.getFont()
        size       = dialog.getSize()
        bold       = dialog.getBold()
        italic     = dialog.getItalic()
        underline  = dialog.getUnderline()
        if rotation   is not NO_CHANGE: self.setRotation(rotation)
        if mirror_h   is not NO_CHANGE: self.setMirrorH(mirror_h)
        if mirror_v   is not NO_CHANGE: self.setMirrorV(mirror_v)
        if autoflip   is not NO_CHANGE: self.setAutoflip(autoflip)
        if align_h    is not NO_CHANGE: self.setAlignH(align_h)
        if align_v    is not NO_CHANGE: self.setAlignV(align_v)
        if origin     is not NO_CHANGE: self.setOrigin(origin)
        if pad_left   is not NO_CHANGE: self.setPadLeft(pad_left)
        if pad_right  is not NO_CHANGE: self.setPadRight(pad_right)
        if pad_top    is not NO_CHANGE: self.setPadTop(pad_top)
        if pad_bottom is not NO_CHANGE: self.setPadBottom(pad_bottom)
        if color      is not NO_CHANGE: self.setTextColor(color)
        if font       is not NO_CHANGE: self.setTextFont(font)
        if size       is not NO_CHANGE: self.setTextSize(size)
        if bold       is not NO_CHANGE: self.setTextBold(bold)
        if italic     is not NO_CHANGE: self.setTextItalic(italic)
        if underline  is not NO_CHANGE: self.setTextUnderline(underline)

    @checked
    def applyDialog(self : Self, dialog : "TextItemDialog") -> None:
        self._applyDialogCommon(dialog)
        text  = dialog.getText()
        block = dialog.getBlock()
        if text  is not NO_CHANGE: self.setText(text)
        if block is not NO_CHANGE: self.setBlock(block)

    @checked
    def ctxMenuItems(self : Self, view : "DrawingView", _spos : QPointF) -> list[QAction | QMenu]:
        """Return context menu items for Text item."""
        items = [
            view.action("Edit...", view.editTextDialog),
            view.separator(),
            self.originMenu(view),
            self.alignmentMenu(view),
            view.separator(),
            view.action(
                "Mirror Horizontal",
                lambda: view.editText(self, mirror_h=not self.mirrorH()),
                checked = self.mirrorH()
            ),
            view.action(
                "Mirror Vertical",
                lambda: view.editText(self, mirror_v=not self.mirrorV()),
                checked = self.mirrorV()
            ),
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
            view.action("Properties...", lambda: view.editItemProperties(self))
        ]
        return items

    def _padding(self : Self) -> tuple[float, float, float, float]:
        return (self._pad_left, self._pad_right, self._pad_top, self._pad_bottom)

    def _syncHandleRect(self : Self, layout : QRectF | None = None) -> None:
        """Map the text layout (constraints and padding) to the handle rectangle."""
        if layout is not None:
            self._brect = layout
        else:
            child = self._child
            if isinstance(child, TextLineRenderer):
                glyph = QGraphicsSimpleTextItem.boundingRect(child)
            else:
                glyph = QGraphicsTextItem.boundingRect(child)
            self._brect = child.mapRectToParent(glyph)
        self._hshape = QPainterPath()
        self._hshape.addRect(self._brect)

class TextRendererMixin(ItemShapeMixin):
    def initRenderer(self : "Self | TextLineRenderer | TextBlockRenderer") -> None:
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, False)
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.initShape()  # empty hit detect shape


    def onSceneOrientationChanged(
        self : "Self | TextLineRenderer | TextBlockRenderer"
    ) -> None:
        """
        Counter-rotate and/or counter-mirror so text stays readable for the
        parent's effective scene rotation and mirror. Pivots at the layout
        rect centre so the flip respects the width/height box.
        """
        parent = self.parentItem()
        if not isinstance(parent, TextItem):
            return
        self.setRotation(0)
        if not parent.autoflip():
            self.setTransform(QTransform())
            self.update()
            return
        a  = parent.sceneRotation()
        mh = parent.sceneMirrorH()
        mv = parent.sceneMirrorV()
        angle = 180.0 if 135 < a <= 315 else 0.0
        sx = -1.0 if mh else 1.0
        sy = -1.0 if mv else 1.0
        pivot = self.transformOriginPoint()
        transform = QTransform()
        transform.translate(pivot.x(), pivot.y())
        transform.rotate(angle)
        transform.scale(sx, sy)
        transform.translate(-pivot.x(), -pivot.y())
        self.setTransform(transform)
        self.update()

    def onSelectionChanged(
        self : "Self | TextLineRenderer | TextBlockRenderer",
        _selected : bool
    ) -> None:
        self._paint_override()

    @checked
    def setFont(
        self : "Self | TextLineRenderer | TextBlockRenderer",
        font : QFont
    ) -> None:
        font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
        super().setFont(font)

    def contextMenuEvent(self : Self,  event : QGraphicsSceneContextMenuEvent) -> None:
        """Bounce context menu event to parent."""
        parent: "TextItem" = self.parentItem()
        parent.contextMenuEvent(event)

    def settingsName(self : Self) -> str:
        return "Text"

    def _setText(
        self : "Self | TextLineRenderer | TextBlockRenderer",
        text : str,
    ) -> None:
        raise NotImplementedError("Subclass must implement this method")

    @staticmethod
    def _autoflipPivot(
        layout_w   : float,
        layout_h   : float,
        child_pos  : QPointF,
    ) -> QPointF:
        """Centre of the layout rect, in child-item coordinates."""
        return QPointF(
            layout_w / 2.0 - child_pos.x(),
            layout_h / 2.0 - child_pos.y(),
        )

    def _paint_selected(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        """
        Paint method override for selected state.
        """
        option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, option, widget)


class TextLineRenderer(TextRendererMixin, QGraphicsSimpleTextItem):
    # instance attributes
    _clip_rect : QRectF | None = None

    @checked
    def __init__(
        self   : Self,
        parent : QGraphicsItem | None = None
    ) -> None:
        super().__init__(parent)
        self.initRenderer()
        self._clip_rect = None

    def itemChange(
        self   : Self,
        change : QGraphicsItem.GraphicsItemChange,
        value  : Any
    ) -> Any:
        """Propagate selection state to parent."""
        match change:
            case self.GraphicsItemChange.ItemSelectedHasChanged:
                parent : TextItem | None = self.parentItem()
                if parent is not None:
                    QGraphicsItem.setSelected(parent, value)
        return super().itemChange(change, value)

    @checked
    def setText(self : Self, text : str) -> None:
        self._setText(text)
        parent : TextItem | None = self.parentItem()
        if parent is not None:
            parent.onGeometryChanged()

    def _setText(self : Self, text : str) -> None:
        super().setText(text)

    def onGeometryChanged(self : Self) -> None:
        parent : TextItem = self.parentItem()
        if parent is None:
            return
        align_h = parent._align_h
        align_v = parent._align_v
        width   = parent._width
        height  = parent._height
        pad_l, pad_r, pad_t, pad_b = parent._padding()
        # update cached bounding rect, accounting for constraints
        urect = QGraphicsSimpleTextItem.boundingRect(self)  # unconstrained rect
        w = (width  if width  >= 0.0 else urect.width())  + pad_l + pad_r
        h = (height if height >= 0.0 else urect.height()) + pad_t + pad_b
        cw = max(w - pad_l - pad_r, 0.0)
        ch = max(h - pad_t - pad_b, 0.0)
        layout = QRectF(0.0, 0.0, w, h)
        # apply clipping if content area is smaller than unconstrained rect
        if cw < urect.width() or ch < urect.height():
            self._clip_rect = layout
        else:
            self._clip_rect = None
        self._paint_override()
        # position to apply alignment within content area
        match align_h:
            case AlignH.LEFT:
                x = pad_l
            case AlignH.CENTER:
                x = pad_l + (cw - urect.width()) / 2
            case AlignH.RIGHT:
                x = pad_l + cw - urect.width()
        match align_v:
            case AlignV.TOP:
                y = pad_t
            case AlignV.MIDDLE:
                y = pad_t + (ch - urect.height()) / 2
            case AlignV.BOTTOM:
                y = pad_t + ch - urect.height()
        child_pos = QPointF(x, y)
        self.setPos(child_pos)
        self.setTransformOriginPoint(self._autoflipPivot(w, h, child_pos))
        self.onSceneOrientationChanged()
        parent._syncHandleRect(layout)

    def color(self : Self) -> QColor:
        return self.brush().color()

    @checked
    def setColor(self : Self, color : QColor) -> None:
        brush = self.brush()
        brush.setColor(color)
        self.setBrush(brush)

    def boundingRect(self: Self) -> QRectF:
        parent : TextItem = self.parentItem()
        return parent.boundingRect()

    def _paint_override(self : Self) -> None:
        """
        Update paint method override for best performance.
        """
        parent : TextItem = self.parentItem()
        if parent is not None and parent.isSelected():
            if self._clip_rect is not None:
                self.paint = self._paint_selected_clipped
            else:
                self.paint = self._paint_selected
        else:
            if "paint" in self.__dict__:
                self.__dict__.pop("paint")

    def _paint_selected_clipped(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        """
        Paint method override for selected state with clipping.
        """
        option.state &= ~QStyle.StateFlag.State_Selected
        painter.save()
        painter.setClipRect(self._clip_rect)
        super().paint(painter, option, widget)
        painter.restore()


class TextBlockRenderer(TextRendererMixin, QGraphicsTextItem):
    @checked
    def __init__(
        self   : Self,
        parent : QGraphicsItem | None = None
    ) -> None:
        super().__init__(parent=parent)
        self.initRenderer()

    def text(self : Self) -> str:
        return self.toPlainText()

    @checked
    def setText(self : Self, text : str) -> None:
        self._setText(text)
        parent : TextItem | None = self.parentItem()
        if parent is not None:
            parent.onGeometryChanged()

    def _setText(self : Self, text : str) -> None:
        self.setPlainText(text)

    def onGeometryChanged(self : Self) -> None:
        parent : TextItem = self.parentItem()
        align_h = parent._align_h
        align_v = parent._align_v
        width   = parent._width
        height  = parent._height
        pad_l, pad_r, pad_t, pad_b = parent._padding()
        # get underlying document
        doc = self.document()
        # apply horizontal alignment
        option = doc.defaultTextOption()
        option.setAlignment(align_h.value)
        doc.setDefaultTextOption(option)
        cursor = QTextCursor(doc)
        cursor.select(QTextCursor.SelectionType.Document)
        block_fmt = cursor.blockFormat()
        block_fmt.setAlignment(align_h.value)
        cursor.setBlockFormat(block_fmt)
        root_frame = doc.rootFrame()
        fmt = root_frame.frameFormat()
        fmt.setMargin(0)  # measure and lay out without frame margins
        root_frame.setFrameFormat(fmt)
        # apply width constraint inside horizontal padding
        if width >= 0.0:
            text_w = max(width - pad_l - pad_r, 0.0)
        elif align_h != AlignH.LEFT:
            # auto width: Qt aligns each line only within its own width unless
            # textWidth is set to the natural (longest-line) document width
            self.setTextWidth(-1.0)
            text_w = QGraphicsTextItem.boundingRect(self).width()
        else:
            text_w = -1.0
        self.setTextWidth(text_w)
        # content height for vertical alignment inside padding
        urect = QGraphicsTextItem.boundingRect(self)  # unconstrained rect
        h = (height if height >= 0.0 else urect.height()) + pad_t + pad_b
        ch = max(h - pad_t - pad_b, 0.0)
        self.setPos(QPointF(0.0, 0.0))
        fmt.setLeftMargin(pad_l)
        fmt.setRightMargin(pad_r)
        fmt.setBottomMargin(pad_b)
        # vertical alignment and top padding via document frame margins
        if height >= 0.0:
            match align_v:
                case AlignV.BOTTOM:
                    align_off = ch - urect.height()
                case AlignV.MIDDLE:
                    align_off = (ch - urect.height()) / 2
                case _:  # Top
                    align_off = 0.0
            fmt.setTopMargin(pad_t + align_off)
        else:
            fmt.setTopMargin(pad_t)
        root_frame.setFrameFormat(fmt)
        w = (width if width >= 0.0 else urect.width()) + pad_l + pad_r
        self.setTransformOriginPoint(self._autoflipPivot(w, h, self.pos()))
        self.onSceneOrientationChanged()
        parent._syncHandleRect(QRectF(0.0, 0.0, w, h))

    def color(self : Self) -> QColor:
        return self.defaultTextColor()

    @checked
    def setColor(self : Self, color : QColor) -> None:
        self.setDefaultTextColor(color)

    def _paint_override(self : Self) -> None:
        parent : TextItem = self.parentItem()
        if parent is not None and parent.isSelected():
            self.paint = self._paint_selected
        else:
            if "paint" in self.__dict__:
                self.__dict__.pop("paint")


class TextItem(DecorativeItem, BaseTextItem):
    pass
