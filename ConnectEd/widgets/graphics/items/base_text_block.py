from typing import Self

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsTextItem, \
                            QWidget, QStyleOptionGraphicsItem, QStyle, QMenu
from PyQt6.QtGui     import QAction, QPainter, QPainterPath

from ..property   import PropertySpec
from ..properties import PropertiesMixin

from .mixin         import ItemMixin
from .mixin.pos     import ItemPosMixin
from .mixin.bound   import ItemBoundMixin
from .mixin.shape   import ItemShapeMixin
from .mixin.handle  import ItemRectHandlesMixin
from .mixin.origin  import ItemOriginMixin
from .mixin.quill   import ItemQuillMixin
from .mixin.outline import ItemOutlineMixin
from .mixin.change  import ItemChangeMixin
from .mixin.clone   import ItemCloneMixin
from .mixin.xml     import ItemXmlMixin
from .mixin.menu    import ItemMenuMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing  import DrawingView


class BaseTextBlock(
    ItemMixin,
    ItemPosMixin,
    ItemBoundMixin,
    ItemShapeMixin,
    ItemRectHandlesMixin,
    ItemOriginMixin,
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
    _ORIGIN_NAME = "Top Left"
    _PROPERTY_SPECS = \
        ItemOriginMixin._PROPERTY_SPECS_ORIGIN | \
        ItemPosMixin._PROPERTY_SPECS_POS | \
        {
            "Text" : PropertySpec(
                type_name = "str",
                getter    = lambda self: self.toPlainText(),
                setter    = lambda self, value: self.setPlainText(value)
            ),
            "Width" : PropertySpec(
                type_name = "float",
                getter    = lambda self: self._rect.width(),
                setter    = lambda self, value: self._crect.setWidth(value)
            ),
            "Height" : PropertySpec(
                type_name = "float",
                getter    = lambda self: self._rect.height(),
                setter    = lambda self, value: self._crect.setHeight(value)
            )
        } | \
        ItemQuillMixin._PROPERTY_SPECS_QUILL

    # instance attributes
    _crect   : QRectF  # constraint rect: -1 (width and/or height) = auto (per Qt)
    _stbrect : QRectF  # tight bounding rect in scene coordinates

    def __init__(self : Self, bare : bool = False) -> None:
        self._crect = QRectF(0, 0, -1, -1)  # auto (fully unconstrained)
        QGraphicsTextItem.__init__(self)
        self.initItem(bare=bare)
        self.onGeometryChange()

    def onGeometryChange(self : Self) -> None:
        if not hasattr(self, "_origin"):  # not fully initialized
            return
        self.prepareGeometryChange()
        # calculate and cache bounding rect, accounting for constraints
        urect = QGraphicsTextItem.boundingRect(self)  # unconstrained rect
        self._brect = QRectF(self._crect)
        if self._crect.width() < 0:  # auto width
            self._brect.setWidth(urect.width())
        if self._crect.height() < 0:  # auto height
            self._brect.setHeight(urect.height())
        # calculate and cache shape
        self._hshape = QPainterPath()
        self._hshape.addRect(self._brect)
        # update origin and position
        old_origin_scene_pos = self.getOriginScenePos()
        self.updateHandles()
        new_origin_scene_pos = self.getOriginScenePos()
        delta = old_origin_scene_pos - new_origin_scene_pos
        self._pos = self.pos() + delta
        self.updateOrigin()
        self.onPositionChange()

    def onPositionChange(
        self : Self | QGraphicsTextItem,
        _ : QPointF | None = None
    ) -> None:
        scene_polygon = self.mapToScene(self._brect)
        self._stbrect = scene_polygon.boundingRect().normalized()

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        return [
            view.action("Edit...", view.ui.editText),
            view.separator(),
            view.action("Appearance...", lambda: view.ui.editAppearance(self)),
            view.action("Properties...", lambda: view.ui.editItemProperties(self))
        ]

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
        option.state &= ~QStyle.StateFlag.State_Selected
        QGraphicsTextItem.paint(self, painter, option, widget)
        if self.isSelected():
            painter.setPen(self.outline.pen)
            painter.drawRect(self._brect)

    def handleRect(self : Self) -> QRectF:
        return self._brect

    def moveHandleBy(self : Self, _ : str, delta : QPointF) -> None:
        """Move the entire Text when any keypoint is dragged."""
        self.setPos(self.pos() + delta)

    def sceneTightBoundingRect(self : Self) -> QRectF:
        return self._stbrect
