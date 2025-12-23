from typing import Self
from abc    import abstractmethod

from PyQt6.QtCore    import Qt, QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsSimpleTextItem, QGraphicsTextItem, \
                            QWidget, QStyleOptionGraphicsItem, QStyle, QMenu
from PyQt6.QtGui     import QPainter, QPainterPath, QAction

from ....core.defs import PITCH

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

from ..property   import PropertySpec
from ..properties import PropertiesMixin

from . import NoChange, NO_CHANGE, AlignH, AlignV

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

    def anchorMenu(self : Self, view : "DrawingView") -> QMenu:
        menu = QMenu("Anchor", view)
        menu.addActions([
            view.action(
                "Top Left",
                lambda: view.ui.editTextBlock(self, anchor="Top Left"),
                checked = self.getOrigin() == "Top Left",
                icon = AnchorTopLeftIcon().get()
            ),
            view.action(
                "Top Center",
                lambda: view.ui.editTextBlock(self, anchor="Top Center"),
                checked = self.getOrigin() == "Top Center",
                icon = AnchorTopCenterIcon().get()
            ),
            view.action(
                "Top Right",
                lambda: view.ui.editTextBlock(self, anchor="Top Right"),
                checked = self.getOrigin() == "Top Right",
                icon = AnchorTopRightIcon().get()
            ),
            view.action(
                "Middle Left",
                lambda: view.ui.editTextBlock(self, anchor="Middle Left"),
                checked = self.getOrigin() == "Middle Left",
                icon = AnchorMiddleLeftIcon().get()
            ),
            view.action(
                "Middle Center",
                lambda: view.ui.editTextBlock(self, anchor="Middle Center"),
                checked = self.getOrigin() == "Middle Center",
                icon = AnchorMiddleCenterIcon().get()
            ),
            view.action(
                "Middle Right",
                lambda: view.ui.editTextBlock(self, anchor="Middle Right"),
                checked = self.getOrigin() == "Middle Right",
                icon = AnchorMiddleRightIcon().get()
            ),
            view.action(
                "Bottom Left",
                lambda: view.ui.editTextBlock(self, anchor="Bottom Left"),
                checked = self.getOrigin() == "Bottom Left",
                icon = AnchorBottomLeftIcon().get()
            ),
            view.action(
                "Bottom Center",
                lambda: view.ui.editTextBlock(self, anchor="Bottom Center"),
                checked = self.getOrigin() == "Bottom Center",
                icon = AnchorBottomCenterIcon().get()
            ),
            view.action(
                "Bottom Right",
                lambda: view.ui.editTextBlock(self, anchor="Bottom Right"),
                checked = self.getOrigin() == "Bottom Right",
                icon = AnchorBottomRightIcon().get()
            )
        ])
        return menu

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

    def setText(self : Self, text : str | NoChange) -> None:
        """Set text and update geometry."""
        if text is NO_CHANGE:
            return
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
            view.action("Edit...", view.ui.editTextLineDialog),
            view.separator(),
            self.anchorMenu(view),
            view.separator(),
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
        self._alignment = qaf.AlignLeft | qaf.AlignTop
        self._width = None
        self._height = None
        self.document().setDocumentMargin(0)  # minimize margin
        self.initItem(bare=bare)
        if pos is not None:
            self.setPos(pos)
        self.onGeometryChange()

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
        _urect = QGraphicsTextItem.boundingRect(self)  # unconstrained rect
        # calculate and cache bounding rect, accounting for constraints
        w = self._width  if self._width  else _urect.width()
        h = self._height if self._height else _urect.height()
        self._brect = QRectF(0.0, 0.0, w, h)
        # apply vertical alignment via document top margin
        if self._height:
            uh = _urect.height()  # unconstrained height
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

    def alignment(self : Self) -> qaf:
        """Return text alignment."""
        return self._alignment

    def setAlignment(self : Self, alignment : qaf) -> None:
        """Set text alignment. Preserves existing horizontal/vertical if not specified."""
        # merge with existing alignment, preserving unspecified components
        h_new = alignment & qaf.AlignHorizontal_Mask
        v_new = alignment & qaf.AlignVertical_Mask
        if hasattr(self, "_alignment"):
            h_old = self._alignment & qaf.AlignHorizontal_Mask
            v_old = self._alignment & qaf.AlignVertical_Mask
        else:
            h_old = qaf.AlignLeft
            v_old = qaf.AlignTop
        self._alignment = (h_new if h_new else h_old) | (v_new if v_new else v_old)
        # horizontal (applied in text renderer)
        doc = self.document()
        opt = doc.defaultTextOption()
        opt.setAlignment(self._alignment & qaf.AlignHorizontal_Mask)
        doc.setDefaultTextOption(opt)
        # vertical is applied in onGeometryChange
        self.onGeometryChange()

    def horizontalAlignment(self : Self) -> AlignH:
        """Return horizontal alignment."""
        h = self._alignment & qaf.AlignHorizontal_Mask
        for a in AlignH:
            if a.value == h:
                return a
        return AlignH.LEFT

    def setHorizontalAlignment(self : Self, alignment : AlignH | qaf) -> None:
        flag = alignment.value if isinstance(alignment, AlignH) else alignment
        self.setAlignment(flag & qaf.AlignHorizontal_Mask)

    def verticalAlignment(self : Self) -> AlignV:
        """Return vertical alignment."""
        v = self._alignment & qaf.AlignVertical_Mask
        for a in AlignV:
            if a.value == v:
                return a
        return AlignV.TOP

    def setVerticalAlignment(self : Self, alignment : AlignV | qaf) -> None:
        flag = alignment.value if isinstance(alignment, AlignV) else alignment
        self.setAlignment(flag & qaf.AlignVertical_Mask)

    def width(self : Self) -> float | None:
        """Return width constraint."""
        return self._width

    def setWidth(self : Self, width : float | None) -> None:
        """Set width constraint (None = auto)."""
        self._width = width
        self.onGeometryChange()

    def height(self : Self) -> float | None:
        """Return height constraint."""
        return self._height

    def setHeight(self : Self, height : float | None) -> None:
        """Set height constraint (None = auto)."""
        self._height = height
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

    def alignmentMenu(self : Self, view : "DrawingView") -> QMenu:
        menu = QMenu("Alignment", view)
        menu.addActions([
            view.action(
                "Left",
                lambda: view.ui.editTextBlock(self, alignment=qaf.AlignLeft),
                checked = self.horizontalAlignment() == qaf.AlignLeft,
                icon = TextAlignLeftIcon().get()
            ),
            view.action(
                "Center",
                lambda: view.ui.editTextBlock(self, alignment=qaf.AlignHCenter),
                checked = self.horizontalAlignment() == qaf.AlignHCenter,
                icon = TextAlignCenterIcon().get()
            ),
            view.action(
                "Right",
                lambda: view.ui.editTextBlock(self, alignment=qaf.AlignRight),
                checked = self.horizontalAlignment() == qaf.AlignRight,
                icon = TextAlignRightIcon().get()
            ),
            view.separator(),
            view.action(
                "Top",
                lambda: view.ui.editTextBlock(self, alignment=qaf.AlignTop),
                checked = self.verticalAlignment() == qaf.AlignTop,
                icon = TextAlignTopIcon().get(),
                enabled = self.height() is not None
            ),
            view.action(
                "Middle",
                lambda: view.ui.editTextBlock(self, alignment=qaf.AlignVCenter),
                checked = self.verticalAlignment() == qaf.AlignVCenter,
                icon = TextAlignMiddleIcon().get(),
                enabled = self.height() is not None
            ),
            view.action(
                "Bottom",
                lambda: view.ui.editTextBlock(self, alignment=qaf.AlignBottom),
                checked = self.verticalAlignment() == qaf.AlignBottom,
                icon = TextAlignBottomIcon().get(),
                enabled = self.height() is not None
            )
        ])
        return menu

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        """Return context menu items for text block."""
        items = [
            view.action("Edit...", view.ui.editTextBlockDialog),
            view.separator(),
            self.alignmentMenu(view),
            self.anchorMenu(view),
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

    def _resizeBy(self : Self, dw : float, dh : float) -> None:
        """Resize the text block by the given deltas."""
        self._width = max(self._brect.width() + dw, PITCH)
        self._height = max(self._brect.height() + dh, PITCH)
        if dw != 0 or dh != 0:
            self.onGeometryChange()
