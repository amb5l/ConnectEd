from typing      import Self, TypeAlias
from dataclasses import dataclass

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsItem, QMenu, \
                            QStyleOptionGraphicsItem, QStyle, QWidget, \
                            QGraphicsSimpleTextItem, QGraphicsTextItem
from PyQt6.QtGui     import QColor, QFont, QAction, QPainterPath, QPainter

from ....core.types import Default, DEFAULT, NoChange, NO_CHANGE, \
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

from ..properties import InherentProperty, PropertiesMixin

from .mixin         import ItemMixin
from .mixin.origin  import ItemOriginMixin
from .mixin.pos     import ItemPosMixin
from .mixin.rotate  import ItemRotateMixin
from .mixin.paint   import ItemPaintMixin
from .mixin.handle  import ItemRectHandlesMixin
from .mixin.quill   import ItemQuillMixin
from .mixin.outline import ItemOutlineMixin
from .mixin.bound   import ItemBoundMixin
from .mixin.shape   import ItemShapeMixin
from .mixin.change  import ItemChangeMixin
from .mixin.clone   import ItemCloneMixin
from .mixin.xml     import ItemXmlMixin
from .mixin.menu    import ItemMenuMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing import DrawingView


@dataclass
class TextState:
    text      : str
    rotation  : float
    flip      : bool
    origin    : RectHandleId
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
    def fromItem(cls, item : "TextItemMixin") -> Self:
        return cls(
            text      = item.text(),
            rotation  = item.rotation(),
            flip      = item.flip(),
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
    rotation  : float            | NoChange = NO_CHANGE
    flip      : bool             | NoChange = NO_CHANGE
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


class TextItemMixin(
    ItemMixin,
    ItemOriginMixin,
    ItemPosMixin,
    ItemRotateMixin,
    ItemPaintMixin,
    ItemRectHandlesMixin,
    ItemQuillMixin,
    ItemOutlineMixin,
    ItemBoundMixin,
    ItemShapeMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemXmlMixin,
    ItemMenuMixin,
    PropertiesMixin
):
    # class attributes
    _ORIGIN = RectHandleId.TOP_LEFT
    _RESIZE_KIND = "text"  # handle kind for text items
    _PROPERTIES_ALIGN = \
        {
            "AlignH" : InherentProperty(
                kind   = DataKind.ALIGN_H,
                getter = lambda self: self.alignH(),
                setter = lambda self, value: self.setAlignH(value)
            ),
            "AlignV" : InherentProperty(
                kind   = DataKind.ALIGN_V,
                valid  = lambda self: self.height() is not None,
                getter = lambda self: self.alignV(),
                setter = lambda self, value: self.setAlignV(value)
            )
        }
    _PROPERTIES_SIZE = \
        {
            "Width" : InherentProperty(
                kind   = DataKind.FLOAT,
                valid  = lambda self: self.width() is not None,
                getter = lambda self: self.width(),
                setter = lambda self, value: self.setWidth(value)
            ),
            "Height" : InherentProperty(
                kind   = DataKind.FLOAT,
                valid  = lambda self: self.height() is not None,
                getter = lambda self: self.height(),
                setter = lambda self, value: self.setHeight(value)
            )
        }

    # instance attributes
    _flip    : bool    # rotation compensation enable
    _angle   : float   # raw (uncompensated) rotation
    _rot_adj : float   # adjustment applied by rotation compensation
    _align_h : AlignH  # horizontal alignment
    _align_v : AlignV  # vertical alignment
    _width   : float   # width constraint
    _height  : float   # height constraint

    def __init__(
        self      : "Self | TextLineItem | TextBlockItem",
        text      : str | None           = None,
        pos       : QPointF | None       = None,
        rotation  : float                = 0.0,
        flip      : bool                 = True,
        origin    : RectHandleId         = RectHandleId.TOP_LEFT,
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
        super().__init__(parent)
        self._flip    = flip
        self._align_h = align_h
        self._align_v = align_v
        self._width   = width
        self._height  = height
        if isinstance(self, TextLineItem):
            self._clip_rect = None
        self.initItem(fresh)
        self.setPos(pos or QPointF(0, 0))
        self.setRotation(rotation)
        self.setOrigin(origin)
        self.setQuillColor(color)
        self.setQuillFamily(family)
        self.setQuillSize(size)
        self.setQuillBold(bold)
        self.setQuillItalic(italic)
        self.setQuillUnderline(underline)
        if text is not None:
            self.setText(text)
        self.onSceneRotationChange()

    def onSelectionChange(self : Self, selected : bool) -> None:
        self._paint_override()

    def onSceneRotationChange(self : Self) -> None:
        if self._flip: self.setRotation()

    def rotation(self : Self) -> float:
        return self._angle

    def setRotation(self : Self, angle : float | None = None) -> None:
        if angle is not None: self._angle = angle
        sa = (self.parentSceneRotation() + self._angle) % 360.0
        self._rot_adj = 180 if self._flip and sa > 135 and sa <= 315 else 0
        super().setRotation(self._angle + self._rot_adj)

    def flip(self : Self) -> bool:
        return self._flip

    def setFlip(self : Self, flip : bool) -> None:
        self._flip = flip
        self.setRotation()

    def alignH(self : Self) -> AlignH:
        return self._align_h

    def setAlignH(self : Self, align_h : AlignH) -> None:
        self._align_h = align_h
        self.onGeometryChange()

    def alignV(self : Self) -> AlignV:
        return self._align_v

    def setAlignV(self : Self, align_v : AlignV) -> None:
        self._align_v = align_v
        self.onGeometryChange()

    def width(self : Self) -> float:
        return self._width

    def setWidth(self : Self, width : float) -> None:
        self._width = width
        self.onGeometryChange()
        self.updateHandlePositions()
        self.updateHandlePaths()
        self.signalPropertyChanges("Width")

    def height(self : Self) -> float:
        return self._height

    def setHeight(self : Self, height : float) -> None:
        self._height = height
        self.onGeometryChange()
        self.updateHandlePositions()
        self.updateHandlePaths()
        self.signalPropertyChanges("Height")

    def setFont(self : Self, font : QFont) -> None:
        super().setFont(font)
        self.onGeometryChange()
        self.updateHandlePositions()

    def handleRect(self : Self) -> QRectF:
        """Return the rectangle used for handles."""
        return self._brect

    def moveHandleBy(self : Self, id : RectHandleId, delta : QPointF) -> None:
        """Resize/move the text as appropriate."""
        origin_name = self.origin().value
        match id:
            case RectHandleId.TOP_LEFT:
                if "Left" in origin_name: self.moveByX(delta.x())
                self.resize(dx=-delta.x())
                if "Top" in origin_name: self.moveByY(delta.y())
                self.resize(dy=-delta.y())
            case RectHandleId.TOP_CENTER:
                if "Top" in origin_name: self.moveByY(delta.y())
                self.resize(dy=-delta.y())
            case RectHandleId.TOP_RIGHT:
                if "Right" in origin_name: self.moveByX(delta.x())
                self.resize(dx=delta.x())
                if "Top" in origin_name: self.moveByY(delta.y())
                self.resize(dy=-delta.y())
            case RectHandleId.MIDDLE_LEFT:
                if "Left" in origin_name: self.moveByX(delta.x())
                self.resize(dx=-delta.x())
            case RectHandleId.MIDDLE_CENTER:
                self.moveBy(delta)
            case RectHandleId.MIDDLE_RIGHT:
                if "Right" in origin_name: self.moveByX(delta.x())
                self.resize(dx=delta.x())
            case RectHandleId.BOTTOM_LEFT:
                if "Left" in origin_name: self.moveByX(delta.x())
                self.resize(dx=-delta.x())
                if "Bottom" in origin_name: self.moveByY(delta.y())
                self.resize(dy=delta.y())
            case RectHandleId.BOTTOM_CENTER:
                if "Bottom" in origin_name: self.moveByY(delta.y())
                self.resize(dy=delta.y())
            case RectHandleId.BOTTOM_RIGHT:
                if "Right" in origin_name: self.moveByX(delta.x())
                self.resize(dx=delta.x())
                if "Bottom" in origin_name: self.moveByY(delta.y())
                self.resize(dy=delta.y())

    def moveByX(self : Self, dx : float) -> None:
        self.setX(self.pos().x() + dx)

    def moveByY(self : Self, dy : float) -> None:
        self.setY(self.pos().y() + dy)

    def resize(self : Self, dx : float = 0.0, dy : float = 0.0) -> None:
        rect = self._brect
        width = self._width if self._width >= 0.0 else rect.width()
        height = self._height if self._height >= 0.0 else rect.height()
        self._width  = max(width  + dx, 0.0)
        self._height = max(height + dy, 0.0)
        self.onGeometryChange()
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

    def _paint_selected(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, option, widget)


class TextLineItem(TextItemMixin, QGraphicsSimpleTextItem):
    _PROPERTIES = \
        {
            "Text" : InherentProperty(
                kind   = DataKind.STR,
                getter = lambda self: self.text(),
                setter = lambda self, value: self.setText(value)
            ),

        } | \
        ItemPosMixin._PROPERTIES_POS | \
        ItemRotateMixin._PROPERTIES_ROTATE | \
        ItemOriginMixin._PROPERTIES_RECT_ORIGIN | \
        TextItemMixin._PROPERTIES_ALIGN | \
        TextItemMixin._PROPERTIES_SIZE | \
        ItemQuillMixin._PROPERTIES_QUILL

    _clip_rect : QRectF | None = None

    def onGeometryChange(self : Self) -> None:
        # update cached bounding rect, accounting for constraints
        urect = QGraphicsSimpleTextItem.boundingRect(self)  # unconstrained rect
        w = self._width  if self._width  >= 0.0 else urect.width()
        h = self._height if self._height >= 0.0 else urect.height()
        self._brect = QRectF(0.0, 0.0, w, h)
        # apply clipping if constraints are smaller than unconstrained rect
        if w < urect.width() or h < urect.height():
            self._clip_rect = self._brect
        else:
            self._clip_rect = None
        self._paint_override()
        # position to apply alignment
        match self._align_h:
            case AlignH.LEFT:
                x = 0
            case AlignH.CENTER:
                x = (w - urect.width()) / 2
            case AlignH.RIGHT:
                x = w - urect.width()
        match self._align_v:
            case AlignV.TOP:
                y = 0
            case AlignV.MIDDLE:
                y = (h - urect.height()) / 2
            case AlignV.BOTTOM:
                y = h - urect.height()
        self.setPos(x, y)
        # update cached hit detect shape
        self._hshape = QPainterPath()
        self._hshape.addRect(self._brect)
        # update transform origin
        self.setTransformOriginPoint(self._brect.center())
        # update
        self.update()

    def setText(self : Self, text : str) -> None:
        super().setText(text)
        self.onGeometryChange()
        self.updateHandlePositions()
        self.signalPropertyChanges("Text")

    def color(self : Self) -> QColor:
        return self.brush().color()

    def setColor(self : Self, color : QColor) -> None:
        brush = self.brush()
        brush.setColor(color)
        self.setBrush(brush)

    def _paint_override(self : Self) -> None:
        if self.isSelected():
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
        option.state &= ~QStyle.StateFlag.State_Selected
        painter.save()
        painter.setClipRect(self._clip_rect)
        super().paint(painter, option, widget)
        painter.restore()


class TextBlockItem(TextItemMixin, QGraphicsTextItem):
    _PROPERTIES = \
        {
            "Text" : InherentProperty(
                kind   = DataKind.TEXT,
                getter = lambda self: self.text(),
                setter = lambda self, value: self.setText(value)
            ),

        } | \
        ItemPosMixin._PROPERTIES_POS | \
        ItemRotateMixin._PROPERTIES_ROTATE | \
        ItemOriginMixin._PROPERTIES_RECT_ORIGIN | \
        TextItemMixin._PROPERTIES_ALIGN | \
        TextItemMixin._PROPERTIES_SIZE | \
        ItemQuillMixin._PROPERTIES_QUILL

    def onGeometryChange(self : Self) -> None:
        # get underlying document
        doc = self.document()
        # apply horizontal alignment
        option = doc.defaultTextOption()
        option.setAlignment(self._align_h.value)
        doc.setDefaultTextOption(option)
        # apply width constraint
        self.setTextWidth(self._width)
        # calculate unconstrained bounding rect (without margins)
        root_frame = doc.rootFrame()
        fmt = root_frame.frameFormat()
        fmt.setMargin(0)  # temporarily remove margins
        root_frame.setFrameFormat(fmt)
        urect = QGraphicsTextItem.boundingRect(self)  # unconstrained rect
        # update cached bounding rect, accounting for constraints
        w = self._width  if self._width  >= 0.0 else urect.width()
        h = self._height if self._height >= 0.0 else urect.height()
        self._brect = QRectF(0.0, 0.0, w, h)
        # if height constrained: apply vertical alignment via document top margin
        if self._height >= 0.0:
            match self._align_v:
                case AlignV.BOTTOM:
                    top_margin = self._height - urect.height()
                case AlignV.MIDDLE:
                    top_margin = (self._height - urect.height()) / 2
                case _:  # Top
                    top_margin = 0
            fmt.setTopMargin(top_margin)
            root_frame.setFrameFormat(fmt)
        # update cached hit detect shape
        self._hshape = QPainterPath()
        self._hshape.addRect(self._brect)
        # update transform origin
        self.setTransformOriginPoint(self._brect.center())
        # update
        self.update()

    def text(self : Self) -> str:
        return super().toPlainText()

    def setText(self : Self, text : str) -> None:
        super().setPlainText(text)
        self.onGeometryChange()
        self.updateHandlePositions()
        self.signalPropertyChanges("Text")

    def color(self : Self) -> QColor:
        return self.defaultTextColor()

    def setColor(self : Self, color : QColor) -> None:
        self.setDefaultTextColor(color)

    def _paint_override(self : Self) -> None:
        if self.isSelected():
            self.paint = self._paint_selected
        else:
            if "paint" in self.__dict__:
                self.__dict__.pop("paint")


TextBothItem : TypeAlias = TextLineItem | TextBlockItem
