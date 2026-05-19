from typing      import Self, Any
from dataclasses import dataclass

from PyQt6.QtCore    import Qt, QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsItem, QMenu, \
                            QStyleOptionGraphicsItem, QStyle, QWidget, \
                            QGraphicsSceneContextMenuEvent, \
                            QGraphicsSimpleTextItem, QGraphicsTextItem
from PyQt6.QtGui     import QColor, QFont, QAction, QPainter, QPainterPath, \
                            QTransform

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

from ..properties import InherentProperty

from .grip import TextResizeGripItem

from .mixin              import PrimaryItemMixin
from .mixin.transform    import ItemTransformMixin
from .mixin.handle       import ItemRectHandlesMixin
from .mixin.shape        import ItemShapeMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing  import DrawingView
    from ..scenes.drawing import DrawingScene


@dataclass
class TextState:
    text      : str
    block     : bool
    rotation  : float
    mirror_h  : bool
    mirror_v  : bool
    autoflip  : bool
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
    def fromItem(cls, item : "TextItem") -> Self:
        return cls(
            text      = item.text(),
            block     = item.block(),
            rotation  = item.rotation(),
            mirror_h  = item.mirrorH(),
            mirror_v  = item.mirrorV(),
            autoflip  = item.autoflip(),
            origin    = item.origin(),
            align_h   = item.alignH(),
            align_v   = item.alignV(),
            width     = item.width(),
            height    = item.height(),
            color     = item.textColor(),
            family    = item.textFont(),
            size      = item.textSize(),
            bold      = item.textBold(),
            italic    = item.textItalic(),
            underline = item.textUnderline()
        )


@dataclass
class TextChange:
    text      : str              | NoChange = NO_CHANGE
    block     : bool             | NoChange = NO_CHANGE
    rotation  : float            | NoChange = NO_CHANGE
    mirror_h  : bool             | NoChange = NO_CHANGE
    mirror_v  : bool             | NoChange = NO_CHANGE
    autoflip  : bool             | NoChange = NO_CHANGE
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
        PrimaryItemMixin._PROPERTIES_TEXT

    # instance attributes
    _child    : "TextLineRenderer | TextBlockRenderer"  # text renderer
    _autoflip : bool                                    # orientation compensation
    _align_h  : AlignH                                  # horizontal alignment
    _align_v  : AlignV                                  # vertical alignment
    _width    : float                                   # width constraint
    _height   : float                                   # height constraint
    _brect    : QRectF                                  # bounding rect

    _text_color     = None  # enable per-item appearance control
    _text_font      = None  # enable per-item appearance control
    _text_size      = None  # enable per-item appearance control
    _text_bold      = None  # enable per-item appearance control
    _text_italic    = None  # enable per-item appearance control
    _text_underline = None  # enable per-item appearance control

    def __init__(
        self      : Self,
        text      : str                  = "",
        block     : bool                 = False,
        pos       : QPointF | None       = None,
        rotation  : float                = 0.0,
        mirror_h  : bool                 = False,
        mirror_v  : bool                 = False,
        autoflip  : bool                 = True,
        origin    : RectHandleId         = RectHandleId.TOP_LEFT,
        align_h   : AlignH               = AlignH.LEFT,
        align_v   : AlignV               = AlignV.TOP,
        width     : float                = -1.0,        # unconstrained
        height    : float                = -1.0,        # unconstrained
        color     : QColor | None        = None,
        family    : str    | None        = None,
        size      : float  | None        = None,
        bold      : bool   | None        = None,
        italic    : bool   | None        = None,
        underline : bool   | None        = None,
        fresh     : bool                 = True,
        parent    : QGraphicsItem | None = None
    ) -> None:
        super().__init__(parent)
        self._autoflip = autoflip
        self._align_h  = align_h
        self._align_v  = align_v
        self._width    = width
        self._height   = height
        self._hshape = QPainterPath()
        self._child = TextBlockRenderer() if block else TextLineRenderer()
        self._child.setParentItem(self)
        self._child.setText(text)
        self.initItem(fresh)
        self.setFlag(self.GraphicsItemFlag.ItemHasNoContents, True)
        self.setPos(pos or QPointF(0, 0))
        self.setRotation(rotation)
        self.setMirrorH(mirror_h)
        self.setMirrorV(mirror_v)
        self.setOrigin(origin)
        self.setTextColor(color)
        self.setTextFont(family)
        self.setTextSize(size)
        self.setTextBold(bold)
        self.setTextItalic(italic)
        self.setTextUnderline(underline)
        self._child.onGeometryChange()
        self.updateHandlePositions()
        self.onSceneRotationChange()

    def onSettingsChanged(self : Self) -> None:
        if (scene := self.scene()) is not None:
            self.onSceneChanged(scene)

    def onSceneChanged(self : Self, scene : "DrawingScene | None") -> None:
        pass

    def onSceneRotationChange(self : Self) -> None:
        self._adjustOrientation()

    def onSceneMirrorChange(self : Self) -> None:
        self._adjustOrientation()

    def block(self : Self) -> bool:
        return isinstance(self._child, TextBlockRenderer)

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
            self._child.onGeometryChange()
            self.updateHandlePositions()
            self.signalPropertyChanges("Block")

    def autoflip(self : Self) -> bool:
        return self._autoflip

    def setAutoflip(self : Self, autoflip : bool) -> None:
        self._autoflip = autoflip
        self._adjustOrientation()
        self.signalPropertyChanges("AutoFlip")

    def text(self : Self) -> str:
        return self._child.text()

    def setText(self : Self, text : str) -> None:
        self._child.setText(text)
        self.updateHandlePositions()
        self.signalPropertyChanges("Text")

    def alignH(self : Self) -> AlignH:
        return self._align_h

    def setAlignH(self : Self, align_h : AlignH) -> None:
        self._align_h = align_h
        self._child.onGeometryChange()
        self.signalPropertyChanges("AlignH")

    def alignV(self : Self) -> AlignV:
        return self._align_v

    def setAlignV(self : Self, align_v : AlignV) -> None:
        self._align_v = align_v
        self._child.onGeometryChange()
        self.signalPropertyChanges("AlignV")

    def width(self : Self) -> float:
        return self._width

    def setWidth(self : Self, width : float) -> None:
        self._width = width
        self._child.onGeometryChange()
        self.updateHandlePositions()
        self.updateGrips()
        self.signalPropertyChanges("Width")

    def height(self : Self) -> float:
        return self._height

    def setHeight(self : Self, height : float) -> None:
        self._height = height
        self._child.onGeometryChange()
        self.updateHandlePositions()
        self.updateGrips()
        self.signalPropertyChanges("Height")

    def color(self : Self) -> QColor:
        return self._child.color()

    def setColor(self : Self, color : QColor) -> None:
        self._child.setColor(color)

    def font(self : Self) -> QFont:
        return self._child.font()

    def setFont(self : Self, font : QFont) -> None:
        self._child.setFont(font)
        self.updateHandlePositions()

    def handleRect(self : Self) -> QRectF:
        """Return the rectangle used for handles."""
        return self._brect

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
        self._child.onGeometryChange()
        self.updateHandlePositions()
        self.updateGrips()

    def resizeY(self : Self, dy : float) -> None:
        rect = self._brect
        height = self._height if self._height >= 0.0 else rect.height()
        self._height = max(height + dy, 0.0)
        self._child.onGeometryChange()
        self.updateHandlePositions()
        self.updateGrips()

    def resize(self : Self, dx : float, dy : float) -> None:
        rect = self._brect
        width = self._width if self._width >= 0.0 else rect.width()
        height = self._height if self._height >= 0.0 else rect.height()
        self._width  = max(width  + dx, 0.0)
        self._height = max(height + dy, 0.0)
        self._child.onGeometryChange()
        self.updateHandlePositions()
        self.updateGrips()

    def updateGrips(self : Self) -> None:
        for handle in self._handles.values():
            handle.grip().updatePath()

    def boundingRect(self : Self) -> QRectF:
        return self._brect

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
                "Mirror Horizontal",
                lambda: view.ui.editText(self, mirror_h=not self.mirrorH()),
                checked = self.mirrorH()
            ),
            view.action(
                "Mirror Vertical",
                lambda: view.ui.editText(self, mirror_v=not self.mirrorV()),
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
            view.action("Properties...", lambda: view.ui.editItemProperties(self))
        ]
        return items

    def _adjustOrientation(self : Self) -> None:
        """
        Counter-rotate and/or counter-mirror the renderer child so text remains
        readable (left-right or up-down) given the item's effective scene
        rotation and mirror state. Both the rotation and the mirror reflection
        are anchored at the renderer's transform origin (rect centre) so the
        text block sits on the mirrored side of the item's origin while still
        reading forwards.
        """
        self._child.setRotation(0)
        if not self._autoflip:
            self._child.setTransform(QTransform())
            return
        a  = self.sceneRotation()
        mh = self.sceneMirrorH()
        mv = self.sceneMirrorV()
        angle = 180.0 if 135 < a <= 315 else 0.0
        sx = -1.0 if mh else 1.0
        sy = -1.0 if mv else 1.0
        pivot = self._child.transformOriginPoint()
        transform = QTransform()
        transform.translate(pivot.x(), pivot.y())
        transform.rotate(angle)
        transform.scale(sx, sy)
        transform.translate(-pivot.x(), -pivot.y())
        self._child.setTransform(transform)


class TextRendererMixin(ItemShapeMixin):
    def initRenderer(self : "Self | TextLineRenderer | TextBlockRenderer") -> None:
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, False)
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.initShape()  # empty hit detect shape

    def onSelectionChanged(
        self : "Self | TextLineRenderer | TextBlockRenderer",
        _selected : bool
    ) -> None:
        self._paint_override()

    def setFont(
        self : "Self | TextLineRenderer | TextBlockRenderer",
        font : QFont
    ) -> None:
        font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
        renderer : "TextLineRenderer | TextBlockRenderer" = super()
        renderer.setFont(font)
        self.onGeometryChange()

    def contextMenuEvent(self : Self,  event : QGraphicsSceneContextMenuEvent) -> None:
        """Bounce context menu event to parent."""
        parent: "TextItem" = self.parentItem()
        parent.contextMenuEvent(event)

    def settingsName(self : Self) -> str:
        return "Text"

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

    def setText(self : Self, text : str) -> None:
        super().setText(text)
        self.onGeometryChange()

    def onGeometryChange(self : Self) -> None:
        parent : TextItem = self.parentItem()
        if parent is None:
            return
        align_h = parent._align_h
        align_v = parent._align_v
        width   = parent._width
        height  = parent._height
        # update cached bounding rect, accounting for constraints
        urect = QGraphicsSimpleTextItem.boundingRect(self)  # unconstrained rect
        w = width  if width  >= 0.0 else urect.width()
        h = height if height >= 0.0 else urect.height()
        rect = QRectF(0.0, 0.0, w, h)
        parent._brect = rect
        # apply clipping if constraints are smaller than unconstrained rect
        if w < urect.width() or h < urect.height():
            self._clip_rect = rect
        else:
            self._clip_rect = None
        self._paint_override()
        # position to apply alignment
        match align_h:
            case AlignH.LEFT:
                x = 0
            case AlignH.CENTER:
                x = (w - urect.width()) / 2
            case AlignH.RIGHT:
                x = w - urect.width()
        match align_v:
            case AlignV.TOP:
                y = 0
            case AlignV.MIDDLE:
                y = (h - urect.height()) / 2
            case AlignV.BOTTOM:
                y = h - urect.height()
        self.setPos(x, y)
        # Transform origin = centre of the (parent-local) constrained rect,
        # re-expressed in this renderer's local coords. The renderer's own
        # setPos(x, y) shifts the two frames apart for non-LEFT/non-TOP
        # alignment, so naively using rect.center() would put the pivot
        # outside the glyph block and break rotation / counter-mirroring.
        self.setTransformOriginPoint(rect.center() - QPointF(x, y))
        # Hit shape covers the full bounding rect (in the parent's local
        # frame), matching every other item type. This keeps empty outlined
        # padding clickable and, crucially, stays valid under mirror /
        # rotation changes - those only retransform the child renderer,
        # never _brect.
        parent._hshape = QPainterPath()
        parent._hshape.addRect(rect)
        # update
        self.update()

    def color(self : Self) -> QColor:
        return self.brush().color()

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
    def __init__(
        self   : Self,
        parent : QGraphicsItem | None = None
    ) -> None:
        super().__init__(parent=parent)
        self.initRenderer()

    def text(self : Self) -> str:
        return self.toPlainText()

    def setText(self : Self, text : str) -> None:
        self.setPlainText(text)
        self.onGeometryChange()

    def onGeometryChange(self : Self) -> None:
        parent : TextItem = self.parentItem()
        align_h = parent._align_h
        align_v = parent._align_v
        width = parent._width
        height = parent._height
        # get underlying document
        doc = self.document()
        # apply horizontal alignment
        option = doc.defaultTextOption()
        option.setAlignment(align_h.value)
        doc.setDefaultTextOption(option)
        # apply width constraint
        self.setTextWidth(width)
        # calculate unconstrained bounding rect (without margins)
        root_frame = doc.rootFrame()
        fmt = root_frame.frameFormat()
        fmt.setMargin(0)  # temporarily remove margins
        root_frame.setFrameFormat(fmt)
        urect = QGraphicsTextItem.boundingRect(self)  # unconstrained rect
        # update cached bounding rect, accounting for constraints
        w = width  if width  >= 0.0 else urect.width()
        h = height if height >= 0.0 else urect.height()
        rect = QRectF(0.0, 0.0, w, h)
        parent._brect = rect
        # update transform origin before mapping (rotation uses it)
        self.setTransformOriginPoint(rect.center())
        # Hit shape covers the full bounding rect (in the parent's local
        # frame), matching every other item type. This keeps empty outlined
        # padding clickable and, crucially, stays valid under mirror /
        # rotation changes - those only retransform the child renderer,
        # never _brect.
        parent._hshape = QPainterPath()
        parent._hshape.addRect(rect)
        # if height constrained: apply vertical alignment via document top margin
        if height >= 0.0:
            match align_v:
                case AlignV.BOTTOM:
                    top_margin = height - urect.height()
                case AlignV.MIDDLE:
                    top_margin = (height - urect.height()) / 2
                case _:  # Top
                    top_margin = 0
            fmt.setTopMargin(top_margin)
            root_frame.setFrameFormat(fmt)
        # update
        self.update()

    def color(self : Self) -> QColor:
        return self.defaultTextColor()

    def setColor(self : Self, color : QColor) -> None:
        self.setDefaultTextColor(color)

    def _paint_override(self : Self) -> None:
        parent : TextItem = self.parentItem()
        if parent is not None and parent.isSelected():
            self.paint = self._paint_selected
        else:
            if "paint" in self.__dict__:
                self.__dict__.pop("paint")
