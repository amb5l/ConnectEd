from typing import Self

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QWidget, QStyleOptionGraphicsItem, QStyle, \
                            QGraphicsSimpleTextItem
from PyQt6.QtGui     import QPainter, QFontMetrics

from ...dialogs.text import TextDialog

from ..properties import PropertySpec, PropertiesMixin

from .anchor_point import APName

from .mixin         import ElementMixin
from .mixin.pos     import ElementPosMixin
from .mixin.anchor  import ElementRectAnchorPointsMixin
from .mixin.origin  import ElementOriginMixin
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


class BaseText(
    ElementMixin,
    ElementPosMixin,
    ElementRectAnchorPointsMixin,
    ElementOriginMixin,
    ElementQuillMixin,
    ElementOutlineMixin,
    ElementChangeMixin,
    ElementCloneMixin,
    ElementXmlMixin,
    ElementMenuMixin,
    PropertiesMixin,
    QGraphicsSimpleTextItem
):
    # class attributes
    _ORIGIN = APName.TopLeft
    _PROPERTY_SPECS_POS = \
        ElementOriginMixin._PROPERTY_SPECS_ORIGIN | \
        ElementPosMixin._PROPERTY_SPECS_POS
    _PROPERTY_SPECS_TEXT = {
        "Text" : PropertySpec(
            type_name = "str",
            getter    = lambda self: self.text(),
            setter    = lambda self, value: self.setText(value)
        )
    }
    _PROPERTY_SPECS_APPEARANCE = \
        ElementQuillMixin._PROPERTY_SPECS_QUILL
    _PROPERTY_SPECS = \
        _PROPERTY_SPECS_POS | \
        _PROPERTY_SPECS_TEXT | \
        _PROPERTY_SPECS_APPEARANCE

    # instance attributes
    _rect  : QRectF  # border rectangle (for keypoints)
    _trect : QRectF  # tight bounding rectangle

    def __init__(
        self : Self,
        pos  : QPointF = QPointF(),
        bare : bool = False
    ) -> None:
        QGraphicsSimpleTextItem.__init__(self, "")
        self.initElement(bare=bare)
        self.setPos(pos)
        self.onGeometryChange()

    def onGeometryChange(self : Self) -> None:
        # Store the current scene position of the origin anchor point
        origin_scene_pos = None
        if hasattr(self, '_origin') and self._origin is not None:
            origin_scene_pos = self.mapToScene(self._origin.pos())

        self._brect = self._rect = super().boundingRect()
        if not self.text():
            self._trect = QRectF()
            return
        font = self.font()
        metrics = QFontMetrics(font)
        baseline_trect = metrics.tightBoundingRect(self.text())
        baseline_y = metrics.ascent()
        self._trect = baseline_trect.translated(0, baseline_y)
        self.updateAnchorPoints()

        # If we had an origin, maintain its scene position
        if origin_scene_pos is not None:
            new_origin_local_pos = self._origin.pos()
            new_origin_scene_pos = self.mapToScene(new_origin_local_pos)
            delta = origin_scene_pos - new_origin_scene_pos
            self._pos = self.pos() + delta

        self.updateOrigin()

    def getMenuItems(self : Self) -> list[str]:
        return ["Edit...", "-", "Properties..."]

    def setText(self, text: str) -> None:
        super().setText(text)
        self.onGeometryChange()

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, option, widget)
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
        dialog = TextDialog(self, view)
        if dialog.exec():
            text, appearance = dialog.getChoice()
            scene : "DrawingScene" = self.scene()
            scene.undo_stack.push(cmdEditText(scene, self, text, appearance))
