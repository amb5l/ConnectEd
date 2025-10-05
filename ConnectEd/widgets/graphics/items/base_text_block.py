from typing import Self

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QWidget, QStyleOptionGraphicsItem, QStyle, \
                            QGraphicsTextItem
from PyQt6.QtGui     import QColor, QPainter, QPainterPath

from ...dialogs.text_block import TextBlockDialog

from ..properties import PropertySpec, PropertiesMixin

from .anchor_point import APName

from .mixin         import ElementMixin
from .mixin.bound   import ElementBoundShapeMixin
from .mixin.origin  import ElementOriginMixin
from .mixin.pos     import ElementPosMixin
from .mixin.anchor  import ElementRectAnchorPointsMixin
from .mixin.quill   import ElementQuillMixin
from .mixin.outline import ElementOutlineMixin
from .mixin.change  import ElementChangeMixin
from .mixin.clone   import ElementCloneMixin
from .mixin.xml     import ElementXmlMixin
from .mixin.menu    import ElementMenuMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing  import DrawingView
    from ..scenes.drawing import DrawingScene


class BaseTextBlock(
    ElementMixin,
    ElementBoundShapeMixin,
    ElementOriginMixin,
    ElementPosMixin,
    ElementRectAnchorPointsMixin,
    ElementQuillMixin,
    ElementOutlineMixin,
    ElementChangeMixin,
    ElementCloneMixin,
    ElementXmlMixin,
    ElementMenuMixin,
    PropertiesMixin,
    QGraphicsTextItem
):
    # class attributes
    _ORIGIN = APName.TopLeft
    _PROPERTY_SPECS = \
        ElementOriginMixin._PROPERTY_SPECS_ORIGIN | \
        ElementPosMixin._PROPERTY_SPECS_POS | \
        {
            "Text" : PropertySpec(
                type_name = "str",
                getter    = lambda self: self.toPlainText(),
                setter    = lambda self, value: self.setPlainText(value)
            )
        } | \
        ElementQuillMixin._PROPERTY_SPECS_QUILL

    # instance attributes
    _rect    : QRectF        # border rectangle (for keypoints)

    def __init__(self : Self, bare : bool = False) -> None:
        QGraphicsTextItem.__init__(self)
        self.initElement(bare=bare)
        self.onGeometryChange()

    def onGeometryChange(self : Self) -> None:
        if not hasattr(self, "_origin"):
            return
        old_origin_scene_pos = self.getOriginScenePos()
        self._brect = self._rect = QGraphicsTextItem.boundingRect(self)
        self._hshape.clear()
        self._hshape.addRect(self._brect)
        self.updateAnchorPoints()
        new_origin_scene_pos = self.getOriginScenePos()
        delta = old_origin_scene_pos - new_origin_scene_pos
        self._pos = self.pos() + delta
        self.updateOrigin()

    def getMenuItems(self : Self) -> list[str]:
        return ["Edit..."]

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

    def moveAnchorPointBy(self : Self, _ : "APName", delta : QPointF) -> None:
        """Move the entire Text when any keypoint is dragged."""
        self.setPos(self.pos() + delta)

    def ctxMenuEdit(
        self    : Self,
        checked : bool,
        view    : "DrawingView"
    ) -> None:
        from ..scenes.drawing.cmd.edit import cmdEditText
        dialog = TextBlockDialog(self, view)
        if dialog.exec():
            text, appearance = dialog.getChoice()
            scene : "DrawingScene" = self.scene()
            scene.undo_stack.push(cmdEditText(scene, self, text, appearance))
