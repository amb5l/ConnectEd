from typing import Self, Optional

from PyQt6.QtCore    import Qt, QPointF, QRectF
from PyQt6.QtWidgets import QWidget, QStyleOptionGraphicsItem, QStyle, \
                            QGraphicsSimpleTextItem
from PyQt6.QtGui     import QPainter, QPen, QBrush

from . import AttrSpec, KP, KPDef, \
              ElementQuillMixin, \
              ElementOutlineMixin, \
              ElementMenuMixin, \
              ElementMixin, \
              cmdPlaceElement


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views import DrawingView

class BaseText(
    ElementQuillMixin,
    ElementOutlineMixin,
    ElementMenuMixin,
    ElementMixin,
    QGraphicsSimpleTextItem
):
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
        ElementQuillMixin._ATTR_SPECS_QUILL
    _KEY_POINTS = [KPDef(k, False, False) for k in KP.__iter__()]
    _ANCHORED = True

    # instance variables
    _pos  : QPointF
    _rect : QRectF

    def __init__(
        self   : Self,
        text   : str = "",
        pos    : QPointF = QPointF(0, 0),
        anchor : KP = KP.TOP_LEFT,
        bare   : bool = False
    ) -> None:
        QGraphicsSimpleTextItem.__init__(self)
        self.initElement(bare=bare)
        self.setAnchor(anchor)
        self.setPos(pos)
        self.setText(text)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable , True)

    def onGeometryChange(self : Self) -> None:
        self.prepareGeometryChange()
        self._rect = super().boundingRect()
        self._kpm.updatePositions()

    def getMenuItems(self : Self) -> list[str]:
        return ["Edit..."]

    def setPos(self : Self, pos : QPointF) -> None:
        self._pos = pos
        super().setPos(pos - self._kpm.anchor_offset)

    def pos(self : Self) -> QPointF:
        return self._pos

    def setText(self, text: str) -> None:
        super().setText(text)
        self.onGeometryChange()
        self.setPos(self._pos)

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setBrush(QBrush(self.quill.current))
        option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, option, widget)
        if self.isSelected():
            painter.setPen(self.outline.pen)
            painter.drawRect(self.boundingRect())

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

    def ctxMenuEdit(
        self    : Self,
        checked : bool,
        view    : "DrawingView"
    ) -> None:
        view.editText(self)

class cmdPlaceBaseText(cmdPlaceElement):
    pass
