__all__ = ["Annotation"]

from typing import Self, Optional

from PyQt6.QtCore    import Qt, QPointF, QRectF
from PyQt6.QtWidgets import QWidget, QStyleOptionGraphicsItem, QStyle
from PyQt6.QtGui     import QPainter, QPen, QBrush, QFontMetrics

from . import CustomGraphicsSimpleTextItem, ElementMixin, TextPref

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .port_pin import Port, BasePin


class Annotation(CustomGraphicsSimpleTextItem, ElementMixin):
    _pos           : QPointF
    _tight_rect    : QRectF
    _anchor_offset : QPointF

    def __init__(
        self   : Self,
        text   : str = "",
        pos    : QPointF = QPointF(0, 0),
        parent : Optional["BasePin | Port"] = None
    ) -> None:
        CustomGraphicsSimpleTextItem.__init__(self, text, parent)
        self.initElement(line=None, fill=None, text=TextPref(), bare=True)
        self._pos = pos
        self._anchor_offset = QPointF(0,0)
        self.onGeometryChange()

    def onGeometryChange(self : Self) -> None:
        self.prepareGeometryChange()
        if not self.text():
            self._tight_rect = QRectF()
            return
        font = self.font()
        metrics = QFontMetrics(font)
        baseline_tight_rect = metrics.tightBoundingRect(self.text())
        baseline_y = metrics.ascent()
        self._tight_rect = baseline_tight_rect.translated(0, baseline_y)
        self._anchor_offset = QPointF(0, self.boundingRect().height() / 2)
        self.setPos(self._pos)

    def setPos(self : Self, pos : QPointF) -> None:
        self._pos = pos
        super().setPos(pos - self._anchor_offset)

    def pos(self : Self) -> QPointF:
        return self._pos

    def setText(self : Self, text : str) -> None:
        super().setText(text)
        self.onGeometryChange()

    def tightBoundingRect(self : Self) -> QRectF:
        return self._tight_rect

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        option.state &= ~QStyle.StateFlag.State_Selected
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setBrush(QBrush(self.appearance.text.current))
        super().paint(painter, option, widget)

