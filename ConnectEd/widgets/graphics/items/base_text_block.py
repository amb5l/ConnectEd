from typing import Self, overload

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsTextItem, \
                            QWidget, QStyleOptionGraphicsItem, QStyle, QMenu
from PyQt6.QtGui     import QAction, QPainter, QPainterPath

from ....core.defs import PITCH

from ..property   import PropertySpec
from ..properties import PropertiesMixin

from .base_rect import BaseRectangleMixin

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
                getter = lambda self: self.toPlainText(),
                setter = lambda self, value: self.setPlainText(value)
            ),
            "Width" : PropertySpec(
                kind   = "float",
                getter = lambda self: self._crect.width(),
                setter = lambda self, value: self._crect.setWidth(value)
            ),
            "Height" : PropertySpec(
                kind   = "float",
                getter = lambda self: self._crect.height(),
                setter = lambda self, value: self._crect.setHeight(value)
            )
        } | \
        ItemQuillMixin._PROPERTY_SPECS_QUILL

    # instance attributes
    _crect   : QRectF  # constraint rect: -1 (width and/or height) = auto (per Qt)
    _stbrect : QRectF  # tight bounding rect in scene coordinates

    def __init__(self : Self, bare : bool = False) -> None:
        self._crect = QRectF(0, 0, -1, -1)  # auto (fully unconstrained)
        QGraphicsTextItem.__init__(self)
        self.document().setDocumentMargin(0)  # minimize margin
        self.initItem(bare=bare)
        self.onGeometryChange()

    def onGeometryChange(self : Self) -> None:
        if not hasattr(self, "_origin"):  # not fully initialized
            return
        self.prepareGeometryChange()
        # apply width constraint to enable text wrapping
        if self._crect.width() >= 0:
            self.setTextWidth(self._crect.width())
        else:
            self.setTextWidth(-1)  # auto width
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
        self.update()  # trigger repaint

    def onPositionChange(
        self : Self | QGraphicsTextItem,
        _ : QPointF | None = None
    ) -> None:
        scene_polygon = self.mapToScene(self._brect)
        self._stbrect = scene_polygon.boundingRect().normalized()

    def setPlainText(self : Self, text : str) -> None:
        QGraphicsTextItem.setPlainText(self, text)
        self.onGeometryChange()

    def text(self : Self) -> str:
        """Convenience method to align with BaseText."""
        return self.toPlainText()

    def setText(self : Self, text : str) -> None:
        """Convenience method to align with BaseText."""
        self.setPlainText(text)

    def setAutoWidth(self : Self, auto : bool) -> None:
        self._crect.setWidth(-1 if auto else self.boundingRect().width())
        self.onGeometryChange()

    def setAutoHeight(self : Self, auto : bool) -> None:
        self._crect.setHeight(-1 if auto else self.boundingRect().height())
        self.onGeometryChange()

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        # clip to constrained dimensions
        if self._crect.width() >= 0 or self._crect.height() >= 0:
            painter.save()
            painter.setClipRect(self._brect)

        option.state &= ~QStyle.StateFlag.State_Selected
        QGraphicsTextItem.paint(self, painter, option, widget)

        if self._crect.width() >= 0 or self._crect.height() >= 0:
            painter.restore()

        if self.isSelected():
            painter.setPen(self.outline.pen)
            painter.drawRect(self._brect)

    @overload
    def setPoints(
        self : Self,
        p1   : QPointF,
        p2   : QPointF
    ) -> None:
        ...

    @overload
    def setPoints(
        self : Self,
        x1   : float | int,
        y1   : float | int,
        x2   : float | int,
        y2   : float | int
    ) -> None:
        ...

    def setPoints(
        self : Self,
        p1_x1 : QPointF | float | int,
        p2_y1 : QPointF | float | int,
        x2    : float | int | None = None,
        y2    : float | int | None = None
    ) -> None:
        """Update position and constraint rect from two corner points."""
        if x2 is None or y2 is None:
            x1 = p1_x1.x()
            y1 = p1_x1.y()
            x2 = p2_y1.x()
            y2 = p2_y1.y()
        else:
            x1 = p1_x1
            y1 = p2_y1
        self.setPos(QPointF(min(x1, x2), min(y1, y2)))
        w = max(abs(x2-x1), PITCH)
        h = max(abs(y2-y1), PITCH)
        if w != self._brect.width():  # width has changed
            self._crect.setWidth(w)
        if h != self._brect.height():  # height has changed
            self._crect.setHeight(h)
        self.onGeometryChange()

    def rect(self : Self) -> QRectF:  # to work with BaseRectangleMixin
        return self._brect

    def handleRect(self : Self) -> QRectF:
        return self._brect

    def moveHandleBy(self : Self, name : str, delta : QPointF) -> None:
        """Resize or move the text block based on which handle is dragged."""
        if name == "Center":  # move the entire item
            self.setPos(self.pos() + delta)
            return
        BaseRectangleMixin.moveHandleBy(self, name, delta)

    def sceneTightBoundingRect(self : Self) -> QRectF:
        return self._stbrect

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        auto_width = self._crect.width() < 0
        auto_height = self._crect.height() < 0
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
