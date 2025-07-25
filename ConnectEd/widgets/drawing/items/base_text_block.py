__all__ = ["BaseTextBlock"]

from typing import Self, Optional

from PyQt6.QtCore    import Qt, QPointF, QRectF
from PyQt6.QtWidgets import QWidget, QStyleOptionGraphicsItem, QStyle, \
                            QGraphicsTextItem
from PyQt6.QtGui     import QColor, QPainter, QPainterPath, \
                            QKeyEvent, QFocusEvent, QTextCursor

from . import AttrSpec, KP, KPDef, QuillPref, \
              ElementKeypointsMixin, \
              ElementQuillMixin, \
              ElementMenuMixin, \
              ElementMixin, \
              cmdPlaceElement

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


class BaseTextBlock(
    ElementKeypointsMixin,
    ElementQuillMixin,
    ElementMenuMixin,
    ElementMixin,
    QGraphicsTextItem
):
    # class variables
    _ATTR_SPECS_TEXT = [
        AttrSpec(
            name      = "Text",
            type_name = "str",
            exists    = lambda self: True,
            getter    = lambda self: self.toPlainText(),
            setter    = lambda self, value: self.setPlainText(value)
        )
    ]
    _ATTR_SPECS = \
        ElementMixin._ATTR_SPECS_BASIC + \
        _ATTR_SPECS_TEXT + \
        ElementQuillMixin._ATTR_SPECS_QUILL
    _KEY_POINTS = [KPDef(k, False, False) for k in KP.__iter__()]

    # instance variables
    _rect  : QRectF
    _shape : QPainterPath

    def __init__(
        self   : Self,
        text   : str = "",
        pos    : QPointF = QPointF(0, 0),
        anchor : KP = KP.TOP_LEFT,
        bare   : bool = False
    ) -> None:
        self._rect = QRectF()
        self._shape = QPainterPath()
        super().__init__(text)
        self.initElement(bare=bare)
        self.setPos(pos)
        self.setAnchor(anchor)
        self.setEditable(False)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable , True)
        self.setFlag(self.GraphicsItemFlag.ItemIsFocusable  , True)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.clearFocus()
            event.accept()
        elif event.key() in (
            Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down,
            Qt.Key.Key_Home, Qt.Key.Key_End
        ):
            cursor = self.textCursor()
            shift = event.modifiers() & Qt.KeyboardModifier.ShiftModifier
            move_mode = QTextCursor.MoveMode.KeepAnchor if shift else \
                QTextCursor.MoveMode.MoveAnchor
            if event.key() == Qt.Key.Key_Left:
                cursor.movePosition(cursor.MoveOperation.Left, move_mode)
            elif event.key() == Qt.Key.Key_Right:
                cursor.movePosition(cursor.MoveOperation.Right, move_mode)
            elif event.key() == Qt.Key.Key_Up:
                cursor.movePosition(cursor.MoveOperation.Up, move_mode)
            elif event.key() == Qt.Key.Key_Down:
                cursor.movePosition(cursor.MoveOperation.Down, move_mode)
            elif event.key() == Qt.Key.Key_Home:
                cursor.movePosition(cursor.MoveOperation.StartOfLine, move_mode)
            elif event.key() == Qt.Key.Key_End:
                cursor.movePosition(cursor.MoveOperation.EndOfLine, move_mode)
            self.setTextCursor(cursor)
            event.accept()
        else:
            super().keyPressEvent(event)
        self._kpm.updatePositions()

    def focusOutEvent(self, event: QFocusEvent) -> None:
        super().focusOutEvent(event)
        scene : Optional["DrawingScene"] = self.scene()
        if scene:
            scene.onTextEditingComplete(self)

    def getMenuItems(self : Self) -> list[str]:
        return ["Appearance..."]

    def setPos(self : Self, pos : QPointF) -> None:
        super().setPos(pos - self._kpm.anchor_offset)

    def pos(self : Self) -> QPointF:
        return super().pos() + self._kpm.anchor_offset

    def setPlainText(self, text: str) -> None:
        super().setPlainText(text)
        self._rect = super().boundingRect()
        self._shape.clear()
        self._shape.addRect(self._rect)
        if hasattr(self, "_kpm"):
            self._kpm.updatePositions()

    def setEditable(self, editable: bool) -> None:
        self.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextEditable if editable else
            Qt.TextInteractionFlag.NoTextInteraction
        )

    def boundingRect(self : Self) -> QRectF:
        if self.hasFocus():
            return super().boundingRect().adjusted(-0.5, -0.5, 0.5, 0.5)
        else:
            return self._rect

    def shape(self : Self) -> QPainterPath:
        if self.hasFocus():
            path = QPainterPath()
            path.addRect(self.boundingRect())
            return path
        else:
            return self._shape

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
            rect = self.boundingRect() #.adjusted(0.5, 0.5, -0.5, -0.5)
            painter.fillRect(rect, QColor(255, 255, 255, 192))
            c = self.defaultTextColor()
            self.setDefaultTextColor(QColor(255, 0, 255))
        if c:
            self.setDefaultTextColor(c)
        super().paint(painter, option, widget)
        if self.isSelected():
            painter.setPen(self.outline.pen)
            painter.drawRect(self.boundingRect())

    def moveKeyPoint(self : Self, kp : KP, delta : QPointF) -> None:
        """Move the entire Text when any keypoint is dragged."""
        self.setPos(self.pos() + delta)

    @classmethod
    def createOrUpdate(
        cls    : Self,
        text   : Optional[str]     = None,
        pos    : Optional[QPointF] = None,
        anchor : Optional[KP]      = None,
        *,
        inst   : Optional[Self] = None
    ) -> "BaseTextBlock":
        inst = cls() if inst is None else inst
        if text is not None:
            inst.setPlainText(text)
        if pos is not None:
            inst.setPos(pos)
        if anchor is not None:
            inst.setAnchor(anchor)
        return inst

    def clone(self : Self) -> Self:
        clone = super().clone()
        clone.setPlainText(self.toPlainText())
        clone.setAnchor(self._kpm.anchor_loc)
        clone.setPos(self.pos())
        return clone

class cmdPlaceBaseTextBlock(cmdPlaceElement):
    pass

