from typing import Self, Optional

from PyQt6.QtCore    import Qt, QPointF, QRectF
from PyQt6.QtWidgets import QWidget, QStyleOptionGraphicsItem, QStyle, \
                            QGraphicsSimpleTextItem
from PyQt6.QtGui     import QPainter, QPen, QBrush, QFontMetrics

from ..properties import PropertySpec, PropertiesMixin

from . import KPLoc, KPDef, \
              ElementMixin, \
              ElementPosMixin, \
              ElementRectKeypointsMixin, \
              ElementAnchorMixin, \
              ElementQuillMixin, \
              ElementOutlineMixin, \
              ElementChangeMixin, \
              ElementCloneMixin, \
              ElementXmlMixin, \
              ElementMenuMixin, \
              cmdPlaceElement


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views import DrawingView

class BaseText(
    ElementMixin,
    ElementPosMixin,
    ElementRectKeypointsMixin,
    ElementAnchorMixin,
    ElementQuillMixin,
    ElementOutlineMixin,
    ElementChangeMixin,
    ElementCloneMixin,
    ElementXmlMixin,
    ElementMenuMixin,
    PropertiesMixin,
    QGraphicsSimpleTextItem
):
    # class variables
    _PROPERTY_SPECS_POS = \
        ElementRectKeypointsMixin._PROPERTY_SPECS_KP | \
        ElementPosMixin._PROPERTY_SPECS_POS
    _PROPERTY_SPECS_TEXT = {
        "Text" : PropertySpec(
            type_name = "str",
            exists    = lambda self: True,
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

    # instance variables
    _trect : QRectF  # tight bounding rect

    def __init__(self : Self, bare : bool = False) -> None:
        QGraphicsSimpleTextItem.__init__(self)
        self.initElement(bare=bare)
        self.onSizeChange()

    def onSizeChange(self : Self) -> None:
        self._kprect = self._brect = super().boundingRect()
        if not self.text():
            self._trect = QRectF()
            return
        font = self.font()
        metrics = QFontMetrics(font)
        baseline_trect = metrics.tightBoundingRect(self.text())
        baseline_y = metrics.ascent()
        self._trect = baseline_trect.translated(0, baseline_y)
        self.updateKeypoints()
        self.updateAnchor()

    def getMenuItems(self : Self) -> list[str]:
        return ["Edit..."]

    def setPos(self : Self, pos : QPointF) -> None:
        super().setPos(pos - self._anchor_offset)

    def pos(self : Self) -> QPointF:
        return self._pos

    def setText(self, text: str) -> None:
        super().setText(text)
        self.onSizeChange()

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

    def moveKeyPoint(self : Self, kp : KPLoc, delta : QPointF) -> None:
        """Move the entire Text when any keypoint is dragged."""
        self.setPos(self.pos() + delta)

    @classmethod
    def createOrUpdate(
        cls    : Self,
        *,
        text   : Optional[str]     = None,
        pos    : Optional[QPointF] = None,
        anchor : Optional[KPLoc]   = None,
        inst   : Optional[Self]    = None
    ) -> "BaseText":
        inst = cls() if inst is None else inst
        if text is not None:
            inst.setText(text)
        if pos is not None:
            inst.setPos(pos)
        if anchor is not None:
            inst.setAnchorLoc(anchor)
        return inst

    def clone(self : Self) -> Self:
        clone = super().clone()
        clone.setText(self.text())
        clone.setAnchorLoc(self.getAnchorLoc())
        clone.setPos(self.pos())
        return clone

    def ctxMenuEdit(
        self    : Self,
        checked : bool,
        view    : "DrawingView"
    ) -> None:
        view.editText(self)

class cmdPlaceBaseText(cmdPlaceElement):
    pass
