from typing import Self
from abc    import abstractmethod

from PyQt6.QtCore    import Qt, QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsSimpleTextItem, QGraphicsTextItem, \
                            QWidget, QStyleOptionGraphicsItem, QStyle, QMenu
from PyQt6.QtGui     import QPainter, QPainterPath, QAction

from ....core.defs import PITCH

from ..property   import PropertySpec
from ..properties import PropertiesMixin

from . import Default, DEFAULT

from .mixin            import ItemMixin
from .mixin.origin     import ItemOriginMixin
from .mixin.pos        import ItemPosMixin
from .mixin.rotate     import ItemRotateMixin
from .mixin.bound      import ItemBoundMixin
from .mixin.shape      import ItemShapeMixin
from .mixin.handle     import ItemRectHandlesMixin
from .mixin.quill      import ItemQuillMixin
from .mixin.outline    import ItemOutlineMixin
from .mixin.change     import ItemChangeMixin
from .mixin.clone      import ItemCloneMixin
from .mixin.xml        import ItemXmlMixin
from .mixin.menu       import ItemMenuMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing  import DrawingView


class BaseTextMixin(
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
    PropertiesMixin
):
    """Base mixin class for text items with common functionality."""

    # class attributes
    _ORIGIN_NAME = "Top Left"
    _PROPERTY_SPECS_POS = \
        ItemOriginMixin._PROPERTY_SPECS_ORIGIN | \
        ItemPosMixin._PROPERTY_SPECS_POS | \
        ItemRotateMixin._PROPERTY_SPECS_ROT
    _PROPERTY_SPECS_TEXT = {
        "Text" : PropertySpec(
            getter = lambda self: self.text(),
            setter = lambda self, value: self.setText(value)
        )
    }
    _PROPERTY_SPECS_APPEARANCE = \
        ItemQuillMixin._PROPERTY_SPECS_QUILL

    # instance attributes
    _stbrect : QRectF  # tight bounding rect in scene coordinates

    @abstractmethod
    def onGeometryChange(self : Self) -> None:
        """Handle geometry changes. Must be implemented by subclasses."""
        ...

    def onPositionChange(
        self : Self,
        _ : QPointF | None = None
    ) -> None:
        """Update scene tight bounding rect when position changes."""
        scene_polygon = self.mapToScene(self.boundingRect())
        self._stbrect = scene_polygon.boundingRect().normalized()

    def sceneTightBoundingRect(self : Self) -> QRectF:
        """Return the tight bounding rect in scene coordinates."""
        return self._stbrect

    @abstractmethod
    def handleRect(self : Self) -> QRectF:
        """Return the rectangle used for handles. Must be implemented by subclasses."""
        ...

    @abstractmethod
    def moveHandleBy(self : Self, name : str, delta : QPointF) -> None:
        """Move or resize based on handle. Must be implemented by subclasses."""
        ...

    @abstractmethod
    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        """Return context menu items. Must be implemented by subclasses."""
        ...


class BaseTextLine(
    BaseTextMixin,
    QGraphicsSimpleTextItem
):
    """Single-line text item."""

    # class attributes
    _AP_RESIZE = [] # no resizing handles
    _PROPERTY_SPECS = \
        BaseTextMixin._PROPERTY_SPECS_POS | \
        BaseTextMixin._PROPERTY_SPECS_TEXT | \
        BaseTextMixin._PROPERTY_SPECS_APPEARANCE

    def __init__(
        self : Self,
        pos  : QPointF | None = None,
        bare : bool = False
    ) -> None:
        QGraphicsSimpleTextItem.__init__(self, "")
        self.initItem(bare=bare)
        if pos is not None:
            self.setPos(pos)

    def onGeometryChange(self : Self) -> None:
        """Handle geometry changes for text line."""
        self.updateHandles()
        self.updateOrigin()
        self.onPositionChange()

    def setText(self : Self, text : str) -> None:
        """Set text and update geometry."""
        super().setText(text)
        if hasattr(self, "properties") and "Text" in self.properties:
            self.properties["Text"].changed.emit(self.text())
        self.onGeometryChange()

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        """Paint the text line with optional selection outline."""
        option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, option, widget)
        if self.isSelected():
            painter.setPen(self.outline.pen)
            painter.drawRect(self.boundingRect())

    def handleRect(self : Self) -> QRectF:
        """Return the bounding rect for handles."""
        return self.boundingRect()

    def moveHandleBy(self : Self, _ : str, delta : QPointF) -> None:
        """Move the entire text when any keypoint is dragged."""
        self.moveBy(delta)

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        """Return context menu items for text line."""
        return [
            view.action("Edit...", view.ui.editTextLine),
            view.separator(),
            view.action("Appearance...", lambda: view.ui.editAppearance(self)),
            view.action("Properties...", lambda: view.ui.editItemProperties(self))
        ]


class BaseTextBlock(
    BaseTextMixin,
    ItemBoundMixin,
    ItemShapeMixin,
    QGraphicsTextItem
):
    """Multi-line text block with optional width/height constraints."""

    # class attributes
    _PROPERTY_SPECS_SIZE = \
        {
            "Width" : PropertySpec(
                kind   = "float",
                getter = lambda self: self._width,
                setter = lambda self, value: setattr(self, "_width", value)
            ),
            "Height" : PropertySpec(
                kind   = "float",
                getter = lambda self: self._height,
                setter = lambda self, value: setattr(self, "_height", value)
            )
        }
    _PROPERTY_SPECS = \
        BaseTextMixin._PROPERTY_SPECS_POS | \
        _PROPERTY_SPECS_SIZE | \
        BaseTextMixin._PROPERTY_SPECS_TEXT | \
        BaseTextMixin._PROPERTY_SPECS_APPEARANCE

    # instance attributes
    _width   : float | Default   # width constraint
    _height  : float | Default   # height constraint
    _align_v : Qt.AlignmentFlag  # vertical alignment

    def __init__(
        self : Self,
        pos  : QPointF | None = None,
        bare : bool = False
    ) -> None:
        self._width   = DEFAULT
        self._height  = DEFAULT
        self._align_v = Qt.AlignmentFlag.AlignTop
        QGraphicsTextItem.__init__(self)
        self.document().setDocumentMargin(0)  # minimize margin
        self.initItem(bare=bare)
        if pos is not None:
            self.setPos(pos)

    def onGeometryChange(self : Self) -> None:
        """Handle geometry changes for text block."""
        if not hasattr(self, "_origin"):  # not fully initialized
            return
        self.prepareGeometryChange()
        # apply width constraint to enable text wrapping
        self.setTextWidth(self._width if self._width != DEFAULT else -1)
        # calculate unconstrained rect (without margins)
        doc = self.document()
        root_frame = doc.rootFrame()
        fmt = root_frame.frameFormat()
        fmt.setMargin(0)  # temporarily remove margins
        root_frame.setFrameFormat(fmt)
        self._urect = QGraphicsTextItem.boundingRect(self)  # unconstrained rect
        # calculate and cache bounding rect, accounting for constraints
        w = self._urect.width() if self._width is DEFAULT else self._width
        h = self._urect.height() if self._height is DEFAULT else self._height
        self._brect = QRectF(0, 0, w, h)
        # apply vertical alignment via document top margin
        if self._height != DEFAULT:
            uh = self._urect.height()  # unconstrained height
            ch = self._brect.height()  # constrained height
            if self._align_v == Qt.AlignmentFlag.AlignBottom:
                top_margin = ch - uh
            elif self._align_v == Qt.AlignmentFlag.AlignVCenter:
                top_margin = (ch - uh) / 2
            else:  # Top
                top_margin = 0
            fmt.setTopMargin(top_margin)
            root_frame.setFrameFormat(fmt)
        # calculate and cache shape
        self._hshape = QPainterPath()
        self._hshape.addRect(self._brect)
        # update
        self.updateHandles()
        self.onPositionChange()
        self.update()
        if hasattr(self, "properties"):
            if "Width" in self.properties:
                self.properties["Width"].changed.emit(self._width)
            if "Height" in self.properties:
                self.properties["Height"].changed.emit(self._height)

    def setOrigin(self : Self, name : str) -> None:
        """Override to handle text alignment."""
        # set horizontal alignment via QTextOption
        doc = self.document()
        opt = doc.defaultTextOption()
        if "Right" in name:
            h_align = Qt.AlignmentFlag.AlignRight
        elif "Center" in name:
            h_align = Qt.AlignmentFlag.AlignHCenter
        else:
            h_align = Qt.AlignmentFlag.AlignLeft
        opt.setAlignment(h_align)
        doc.setDefaultTextOption(opt)
        # save vertical alignment for use in onGeometryChange()
        if "Bottom" in name:
            self._align_v = Qt.AlignmentFlag.AlignBottom
        elif "Middle" in name:
            self._align_v = Qt.AlignmentFlag.AlignVCenter
        else:
            self._align_v = Qt.AlignmentFlag.AlignTop
        # set origin handle
        super().setOrigin(name)
        # update margins based on new alignment
        self.onGeometryChange()

    def setPlainText(self : Self, text : str) -> None:
        """Set plain text and update geometry."""
        QGraphicsTextItem.setPlainText(self, text)
        if hasattr(self, "properties") and "Text" in self.properties:
            self.properties["Text"].changed.emit(self.text())
        self.onGeometryChange()

    def text(self : Self) -> str:
        """Convenience method to align with BaseTextLine."""
        return self.toPlainText()

    def setText(self : Self, text : str) -> None:
        """Convenience method to align with BaseTextLine."""
        self.setPlainText(text)

    def setAutoWidth(self : Self, auto : bool) -> None:
        """Set whether width should auto-adjust."""
        self._width = DEFAULT if auto else self.boundingRect().width()
        self.onGeometryChange()

    def setAutoHeight(self : Self, auto : bool) -> None:
        """Set whether height should auto-adjust."""
        self._height = DEFAULT if auto else self.boundingRect().height()
        self.onGeometryChange()

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        """Override selected appearance."""
        option.state &= ~QStyle.StateFlag.State_Selected
        QGraphicsTextItem.paint(self, painter, option, widget)
        if self.isSelected():
            painter.setPen(self.outline.pen)
            painter.drawRect(self._brect)

    def rect(self : Self) -> QRectF:
        """Return the bounding rect (for BaseRectangleMixin compatibility)."""
        return self._brect

    def handleRect(self : Self) -> QRectF:
        """Return the rectangle used for handles."""
        return self._brect

    def moveHandleBy(self : Self, name : str, delta : QPointF) -> None:
        """Resize or move the text block based on which handle is dragged."""
        match name:
            case "Top Left":
                self.setPos(self.pos() + delta)
                self._resizeBy(-delta.x(), -delta.y())
            case "Top Center":
                self.setPos(self.pos() + QPointF(0, delta.y()))
                self._resizeBy(0, -delta.y())
            case "Top Right":
                self.setPos(self.pos() + QPointF(0, delta.y()))
                self._resizeBy(delta.x(), -delta.y())
            case "Middle Left":
                self.setPos(self.pos() + QPointF(delta.x(), 0))
                self._resizeBy(-delta.x(), 0)
            case "Middle Center":
                self.setPos(self.pos() + delta)
            case "Middle Right":
                self._resizeBy(delta.x(), 0)
            case "Bottom Left":
                self.setPos(self.pos() + QPointF(delta.x(), 0))
                self._resizeBy(-delta.x(), delta.y())
            case "Bottom Center":
                self._resizeBy(0, delta.y())
            case "Bottom Right":
                self._resizeBy(delta.x(), delta.y())

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        """Return context menu items for text block."""
        auto_width = self._width is DEFAULT
        auto_height = self._height is DEFAULT
        items = [
            view.action("Edit...", view.ui.editTextBlock),
            view.separator(),
            view.action(
                "Auto Width", lambda: self.setAutoWidth(not auto_width), auto_width
            ),
            view.action(
                "Auto Height", lambda: self.setAutoHeight(not auto_height), auto_height
            ),
            view.separator(),
            view.action("Appearance...", lambda: view.ui.editAppearance(self)),
            view.action("Properties...", lambda: view.ui.editItemProperties(self))
        ]
        return items

    def _resizeBy(self : Self, dw : float, dh : float) -> None:
        """Resize the text block by the given deltas."""
        self._width = max(self._brect.width() + dw, PITCH)
        self._height = max(self._brect.height() + dh, PITCH)
        if dw != 0 or dh != 0:
            self.onGeometryChange()
