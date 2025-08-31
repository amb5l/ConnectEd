from typing import Self, Optional

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QWidget, QStyleOptionGraphicsItem, QStyle, \
                            QGraphicsSimpleTextItem
from PyQt6.QtGui     import QPainter, QFontMetrics

from ...dialogs.text import TextDialog

from ..properties import PropertySpec, PropertiesMixin

from . import APType, \
              ElementMixin, \
              ElementPosMixin, \
              ElementRectAnchorPointsMixin, \
              ElementOriginMixin, \
              ElementQuillMixin, \
              ElementOutlineMixin, \
              ElementChangeMixin, \
              ElementCloneMixin, \
              ElementXmlMixin, \
              ElementMenuMixin

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
    _AP_TYPES = { k : APType.Mover \
            for k in ElementRectAnchorPointsMixin._ANCHOR_POINTS.keys() }
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
        self.updateHandlesVisibility()

    def onGeometryChange(self : Self) -> None:
        self._brect = self._rect = super().boundingRect()
        if not self.text():
            self._trect = QRectF()
            return
        font = self.font()
        metrics = QFontMetrics(font)
        baseline_trect = metrics.tightBoundingRect(self.text())
        baseline_y = metrics.ascent()
        self._trect = baseline_trect.translated(0, baseline_y)
        self.updateKeypoints()
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

    def moveAnchorPointBy(self : Self, _ : str, delta : QPointF) -> None:
        """Move the entire Text when any keypoint is dragged."""
        self.setPos(self.pos() + delta)

    @classmethod
    def createOrUpdate(
        cls    : Self,
        *,
        text   : Optional[str]     = None,
        pos    : Optional[QPointF] = None,
        anchor : Optional[str]     = None,
        inst   : Optional[Self]    = None
    ) -> "BaseText":
        inst = cls() if inst is None else inst
        if text is not None:
            inst.setText(text)
        if pos is not None:
            inst.setPos(pos)
        if anchor is not None:
            inst.setOrigin(anchor)
        return inst

    def ctxMenuEdit(
        self    : Self,
        checked : bool,
        view    : "DrawingView"
    ) -> None:
        from ..scenes.drawing.cmd.edit import cmdEditText
        dialog = TextDialog(self)
        if dialog.exec():
            text, appearance = dialog.getChoice()
            scene : "DrawingScene" = self.scene()
            scene.undo_stack.push(cmdEditText(scene, self, text, appearance))
