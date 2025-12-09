from typing import Self
from abc    import abstractmethod

from PyQt6.QtCore    import Qt, QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsSimpleTextItem, QGraphicsTextItem, \
                            QWidget, QStyleOptionGraphicsItem, QStyle, QMenu
from PyQt6.QtGui     import QPainter, QPainterPath, QAction

from ....core.defs import PITCH

from ..property   import PropertySpec
from ..properties import PropertiesMixin

from .mixin            import ItemMixin
from .mixin.pos_rot    import ItemPosRotMixin
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
    ItemPosRotMixin,
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
    _PROPERTY_SPECS_TEXT = {
        "Text" : PropertySpec(
            getter = lambda self: self.text(),
            setter = lambda self, value: self.setText(value)
        )
    }

    @abstractmethod
    def onGeometryChange(self : Self) -> None:
        """Handle geometry changes. Must be implemented by subclasses."""
        ...

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
        ItemPosRotMixin._PROPERTY_SPECS_POS_ROT | \
        BaseTextMixin._PROPERTY_SPECS_TEXT | \
        ItemQuillMixin._PROPERTY_SPECS_QUILL

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
        self.onSceneBoundRectChange()

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


qaf = Qt.AlignmentFlag

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
                valid  = lambda self: self._width is not None,
                getter = lambda self: self._width,
                setter = lambda self, value: setattr(self, "_width", value)
            ),
            "Height" : PropertySpec(
                kind   = "float",
                valid  = lambda self: self._height is not None,
                getter = lambda self: self._height,
                setter = lambda self, value: setattr(self, "_height", value)
            )
        }
    _PROPERTY_SPECS = \
        ItemPosRotMixin._PROPERTY_SPECS_POS_ROT | \
        _PROPERTY_SPECS_SIZE | \
        BaseTextMixin._PROPERTY_SPECS_TEXT | \
        ItemQuillMixin._PROPERTY_SPECS_QUILL

    # instance attributes
    _alignment : qaf           # alignment
    _width     : float | None  # width constraint
    _height    : float | None  # height constraint

    def __init__(
        self : Self,
        pos  : QPointF | None = None,
        bare : bool = False
    ) -> None:
        QGraphicsTextItem.__init__(self)
        self.setAlignment(qaf.AlignLeft | qaf.AlignTop)
        self._width   = None
        self._height  = None
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
        self.setTextWidth(self._width if self._width else -1)
        # calculate unconstrained rect (without margins)
        doc = self.document()
        root_frame = doc.rootFrame()
        fmt = root_frame.frameFormat()
        fmt.setMargin(0)  # temporarily remove margins
        root_frame.setFrameFormat(fmt)
        self._urect = QGraphicsTextItem.boundingRect(self)  # unconstrained rect
        # calculate and cache bounding rect, accounting for constraints
        w = self._width  if self._width  else self._urect.width()
        h = self._height if self._height else self._urect.height()
        self._brect = QRectF(0.0, 0.0, w, h)
        # apply vertical alignment via document top margin
        if self._height:
            uh = self._urect.height()  # unconstrained height
            ch = self._brect.height()  # constrained height
            match self._alignment & qaf.AlignVertical_Mask:
                case qaf.AlignBottom:
                    top_margin = ch - uh
                case qaf.AlignVCenter:
                    top_margin = (ch - uh) / 2
                case _:  # Top
                    top_margin = 0
            fmt.setTopMargin(top_margin)
            root_frame.setFrameFormat(fmt)
        # calculate and cache shape
        self._hshape = QPainterPath()
        self._hshape.addRect(self._brect)
        # update
        self.updateHandles()
        self.onSceneBoundRectChange()
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
            h_align = qaf.AlignRight
        elif "Center" in name:
            h_align = qaf.AlignHCenter
        else:
            h_align = qaf.AlignLeft
        opt.setAlignment(h_align)
        doc.setDefaultTextOption(opt)
        # save vertical alignment for use in onGeometryChange()
        if "Bottom" in name:
            self._align_v = qaf.AlignBottom
        elif "Middle" in name:
            self._align_v = qaf.AlignVCenter
        else:
            self._align_v = qaf.AlignTop
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
        self._width = None if auto else self.boundingRect().width()
        self.onGeometryChange()

    def setAutoHeight(self : Self, auto : bool) -> None:
        """Set whether height should auto-adjust."""
        self._height = None if auto else self.boundingRect().height()
        self.onGeometryChange()

    def alignment(self : Self) -> qaf:
        """Return text alignment."""
        return self._alignment

    def setAlignment(self : Self, alignment : qaf) -> None:
        """Set text alignment."""
        self._alignment = alignment
        # horizontal (applied in text renderer)
        doc = self.document()
        opt = doc.defaultTextOption()
        opt.setAlignment(alignment & qaf.AlignHorizontal_Mask)
        doc.setDefaultTextOption(opt)
        # vertical is applied in onGeometryChange

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
        align_menu = QMenu("Align")
        align_menu_items = [
            view.action(
                "Left", lambda: self.setAlignment(qaf.AlignLeft)),
        ]
        align_menu.addAction(view.action("Left", lambda: self.setAlignment(qaf.AlignLeft)))
        auto_width = self._width is None
        auto_height = self._height is None
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
