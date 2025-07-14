from typing import Self, Optional

from PyQt6.QtCore    import Qt, QPointF, QRectF
from PyQt6.QtWidgets import QWidget, QStyleOptionGraphicsItem, QStyle
from PyQt6.QtGui     import QPainter, QPen, QBrush

from . import CustomGraphicsSimpleTextItem, ElementMixin, TextPref, \
              AttrSpec, KP, KPDef, cmdPlaceElement

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingView


class BaseTextLine(CustomGraphicsSimpleTextItem, ElementMixin):
    # class variables
    _ATTR_SPECS = ElementMixin._ATTR_SPECS + [
        AttrSpec(
            name      = "Anchor",
            type_name = "KP",
            exists    = lambda self: True,
            getter    = lambda self: self.anchor(),
            setter    = lambda self, value: self.setAnchor(value)
        ),
        AttrSpec(
            name      = "Text",
            type_name = "str",
            exists    = lambda self: True,
            getter    = lambda self: self.text(),
            setter    = lambda self, value: self.setText(value)
        )
    ] + ElementMixin._ATTR_SPECS_APPEARANCE_TEXT
    _KEY_POINTS = [KPDef(k, True, False) for k in KP.__iter__()]

    def __init__(
        self   : Self,
        text   : str = "",
        pos    : QPointF = QPointF(0, 0),
        anchor : KP = KP.TOP_LEFT,
        bare   : bool = False
    ) -> None:
        super().__init__(text)
        self.initElement(line=None, fill=None, text=TextPref(), bare=bare)
        self.setPos(pos)
        self.setAnchor(anchor)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable , True)

    def setPos(self : Self, pos : QPointF) -> None:
        super().setPos(pos - self._kpm.anchor_offset)

    def pos(self : Self) -> QPointF:
        return super().pos() + self._kpm.anchor_offset

    def update(self : Self) -> None:
        super().update()
        if hasattr(self, "_kpm"):
            self._kpm.updatePositions()

    def setText(self, text: str) -> None:
        super().setText(text)
        self.update()

    def KPRect(self : Self) -> QRectF:
        return self.boundingRect()

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setBrush(QBrush(self.appearance.text.current))
        option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, option, widget)
        if self.isSelected():
            painter.setPen(self.appearance.outline.pen)
            painter.drawRect(self.boundingRect())

    def setKPVisible(self : Self, visible : bool) -> None:
        self._kpm.setVisible(visible)

    def moveKeyPoint(self : Self, kp : KP, delta : QPointF) -> None:
        """Move the entire TextLine when any keypoint is dragged."""
        self.setPos(self.pos() + delta)

    @classmethod
    def createOrUpdate(
        cls  : Self,
        *args,
        inst : Optional[Self] = None
    ) -> "BaseTextLine":
        inst = cls() if inst is None else inst
        for arg in args:
            match arg:
                case str() as text:
                    inst.setText(text)
                case QPointF() as pos:
                    inst.setPos(pos)
                case KP() as anchor:
                    inst.setAnchor(anchor)
                case _:
                    raise TypeError(f"Unsupported argument type: {type(arg)}")
        return inst

    def clone(self : Self) -> Self:
        clone = super().clone()
        clone.setText(self.text())
        clone.setAnchor(self._kpm.anchor_loc)
        return clone

class cmdPlaceBaseTextLine(cmdPlaceElement):
    element : BaseTextLine
