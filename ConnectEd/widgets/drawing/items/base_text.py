from typing import Self, Optional

from PyQt6.QtCore    import Qt, QPointF, QRectF
from PyQt6.QtWidgets import QWidget, QStyleOptionGraphicsItem, QStyle
from PyQt6.QtGui     import QPainter, QPen, QBrush

from . import CustomGraphicsSimpleTextItem, ElementMixin, TextPref, \
              AttrSpec, KP, KPDef, cmdPlaceElement


class BaseText(CustomGraphicsSimpleTextItem, ElementMixin):
    # class variables
    _ATTR_SPECS_TEXT = [
        AttrSpec(
            name      = "Text",
            type_name = "str",
            exists    = lambda self: True,
            getter    = lambda self: self.text(),
            setter    = lambda self, value: self.setText(value)
        )
    ]
    _ATTR_SPECS = \
        ElementMixin._ATTR_SPECS_BASIC + \
        _ATTR_SPECS_TEXT + \
        ElementMixin._ATTR_SPECS_APPEARANCE_TEXT
    _KEY_POINTS = [KPDef(k, True, False) for k in KP.__iter__()]
    _ANCHORED = True

    def __init__(
        self   : Self,
        text   : str = "",
        pos    : QPointF = QPointF(0, 0),
        anchor : KP = KP.TOP_LEFT,
        bare   : bool = False
    ) -> None:
        CustomGraphicsSimpleTextItem.__init__(self, text)
        self.initElement(line=None, fill=None, text=TextPref(), bare=bare)
        self.setAnchor(anchor)
        self.setPos(pos)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable , True)

    def setPos(self : Self, pos : QPointF) -> None:
        super().setPos(pos - self._kpm.anchor_offset)

    def pos(self : Self) -> QPointF:
        return super().pos() + self._kpm.anchor_offset

    def setText(self, text: str) -> None:
        current_pos = self.pos()
        super().setText(text)
        self._kpm.updatePositions()
        self.setPos(current_pos)

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
        """Move the entire Text when any keypoint is dragged."""
        self.setPos(self.pos() + delta)

    @classmethod
    def createOrUpdate(
        cls  : Self,
        *args,
        inst : Optional[Self] = None
    ) -> "BaseText":
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
        clone.setPos(self.pos())
        return clone

class cmdPlaceBaseText(cmdPlaceElement):
    pass
