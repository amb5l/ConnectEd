from typing import Self

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsTextItem, \
                            QWidget, QStyleOptionGraphicsItem, QStyle, QMenu
from PyQt6.QtGui     import QColor, QPainter, QAction

from ....app import window

from ..properties import PropertySpec, PropertiesMixin

from .mixin         import ItemMixin
from .mixin.origin  import ItemOriginMixin
from .mixin.pos     import ItemPosMixin
from .mixin.anchor  import ItemRectAnchorPointsMixin
from .mixin.quill   import ItemQuillMixin
from .mixin.outline import ItemOutlineMixin
from .mixin.change  import ItemChangeMixin
from .mixin.clone   import ItemCloneMixin
from .mixin.xml     import ItemXmlMixin
from .mixin.menu    import ItemMenuMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing  import DrawingView
    from ..scenes.drawing import DrawingScene


class BaseTextBlock(
    ItemMixin,
    ItemOriginMixin,
    ItemPosMixin,
    ItemRectAnchorPointsMixin,
    ItemQuillMixin,
    ItemOutlineMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemXmlMixin,
    ItemMenuMixin,
    PropertiesMixin,
    QGraphicsTextItem
):
    # class attributes
    _ORIGIN = "Top Left"
    _PROPERTY_SPECS = \
        ItemOriginMixin._PROPERTY_SPECS_ORIGIN | \
        ItemPosMixin._PROPERTY_SPECS_POS | \
        {
            "Text" : PropertySpec(
                type_name = "str",
                getter    = lambda self: self.toPlainText(),
                setter    = lambda self, value: self.setPlainText(value)
            )
        } | \
        ItemQuillMixin._PROPERTY_SPECS_QUILL

    # instance attributes
    _ap_rect : QRectF  # anchor point rectangle

    def __init__(self : Self, bare : bool = False) -> None:
        QGraphicsTextItem.__init__(self)
        self.initItem(bare=bare)
        self.onGeometryChange()

    def onGeometryChange(self : Self) -> None:
        if not hasattr(self, "_origin"):
            return
        old_origin_scene_pos = self.getOriginScenePos()
        self._ap_rect = self.boundingRect()
        self.updateAnchorPoints()
        new_origin_scene_pos = self.getOriginScenePos()
        delta = old_origin_scene_pos - new_origin_scene_pos
        self._pos = self.pos() + delta
        self.updateOrigin()

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        return [
            view.action("Edit...", view.ui.editText),
            view.separator()
        ] + super().ctxMenuItems()

    def setPlainText(self : Self, text : str) -> None:
        QGraphicsTextItem.setPlainText(self, text)
        self.onGeometryChange()

    def text(self : Self) -> str:
        """Convenience method to align with BaseText."""
        return self.toPlainText()

    def setText(self : Self, text : str) -> None:
        """Convenience method to align with BaseText."""
        self.setPlainText(text)

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        # override selected appearance
        c = None
        option.state &= ~QStyle.StateFlag.State_Selected
        if option.state & QStyle.StateFlag.State_HasFocus:
            rect = self.boundingRect()
            painter.fillRect(rect, QColor(255, 255, 255, 192))
            c = self.defaultTextColor()
            self.setDefaultTextColor(QColor(255, 0, 255))
        if c:
            self.setDefaultTextColor(c)
        QGraphicsTextItem.paint(self, painter, option, widget)
        if self.isSelected():
            painter.setPen(self.outline.pen)
            painter.drawRect(self.boundingRect())

    def moveAnchorPointBy(self : Self, _ : str, delta : QPointF) -> None:
        """Move the entire Text when any keypoint is dragged."""
        self.setPos(self.pos() + delta)
