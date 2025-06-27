from typing import Self, Optional

from PyQt6.QtCore    import Qt, QPointF, QRectF
from PyQt6.QtWidgets import QWidget, QStyleOptionGraphicsItem, QStyle
from PyQt6.QtGui     import QPainter, QPen, QBrush

from . import CustomGraphicsSimpleTextItem, ElementMixin, TextPref, \
              KPManager, KPLoc, KPDef, \
              cmdPlaceElement

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingView


class BaseTextLine(CustomGraphicsSimpleTextItem, ElementMixin):
    # class variables
    _XML_ATTRS = ElementMixin._XML_ATTRS | {
        "text" : (
            "str",
            lambda self: True,
            lambda self, value: self.setText(value),
            lambda self: self.text()
        )
    }
    _MENU_ITEM_NAMES = [
        "Appearance..."
    ]

    # instance variables
    _kpm : KPManager

    def __init__(
        self   : Self,
        text   : str = "",
        pos    : QPointF = QPointF(0, 0),
        anchor : KPLoc = KPLoc.TOP_LEFT
    ) -> None:
        super().__init__(text)
        self.initElement(line=None, fill=None, text=TextPref())
        self._kpm = KPManager(
            self,
            [KPDef(k, True, False) for k in KPLoc],
            KPLoc.TOP_LEFT
        )
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

    def setAnchor(self : Self, anchor : KPLoc = KPLoc.TOP_LEFT) -> None:
        self._kpm.setAnchor(anchor)

    def setKPVisible(self : Self, visible : bool) -> None:
        self._kpm.setVisible(visible)

    def moveKeyPoint(self : Self, kp : KPLoc, delta : QPointF) -> None:
        """Move the entire TextLine when any keypoint is dragged."""
        self.setPos(self.pos() + delta)

    def ctxMenuAppearance(
        self    : Self,
        checked : bool,
        view    : "DrawingView"
    ) -> None:
        view.editAppearance(self)

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
                case KPLoc() as anchor:
                    inst.setAnchor(anchor)
                case _:
                    raise TypeError(f"Unsupported argument type: {type(arg)}")
        return inst

    def clone(self : Self) -> Self:
        """Create a clone of this text block with a new UUID."""
        clone = super().clone()
        # Copy text-specific properties
        clone.setPlainText(self.toPlainText())
        clone.setAnchor(self._kpm.anchor_loc)
        return clone

class cmdPlaceBaseTextLine(cmdPlaceElement):
    element : BaseTextLine
