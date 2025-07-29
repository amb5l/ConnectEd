__all__ = ["BaseTextBlock"]

from typing import Self, Optional

from PyQt6.QtCore    import Qt, QPointF, QRectF
from PyQt6.QtWidgets import QWidget, QStyleOptionGraphicsItem, QStyle, \
                            QGraphicsTextItem
from PyQt6.QtGui     import QColor, QPainter, QPainterPath, \
                            QKeyEvent, QFocusEvent, QTextCursor

from ..properties import PropertySpec, PropertiesMixin

from . import KPLoc, \
              ElementMixin, \
              ElementBoundShapeMixin, \
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
    from .. import DrawingScene


class BaseTextBlock(
    ElementMixin,
    ElementBoundShapeMixin,
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
    QGraphicsTextItem
):
    # class variables
    _PROPERTY_SPECS = \
        ElementRectKeypointsMixin._PROPERTY_SPECS_KP | \
        ElementPosMixin._PROPERTY_SPECS_POS | \
        {
            "Text" : PropertySpec(
                type_name = "str",
                exists    = lambda self: True,
                getter    = lambda self: self.toPlainText(),
                setter    = lambda self, value: self.setPlainText(value)
            )
        } | \
        ElementQuillMixin._PROPERTY_SPECS_QUILL

    # instance variables
    _brectf  : QRectF        # bounding rect when has focus
    _hshapef : QPainterPath  # hit detect shape when has focus

    def __init__(self : Self, bare : bool = False) -> None:
        super().__init__()
        self.initElement(bare=bare)
        self.setEditable(False)
        self.setFlag(self.GraphicsItemFlag.ItemIsFocusable, True)
        self._brectf = QRectF()
        self._hshapef = QPainterPath()
        self.onSizeChange()

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
        self.onSizeChange()  # text change means size change
        print(self.toPlainText(), self._brect, super().boundingRect())

    def focusOutEvent(self, event: QFocusEvent) -> None:
        super().focusOutEvent(event)
        scene : Optional["DrawingScene"] = self.scene()
        if scene:
            scene.onTextEditingComplete(self)

    def onAppearanceChange(self : Self) -> None:
        self.onSizeChange()

    def onSizeChange(self : Self) -> None:
        self.prepareGeometryChange()
        self._kprect = self._brect = super().boundingRect()
        self._brectf = self._brect.adjusted(-0.5, -0.5, 0.5, 0.5)
        self._hshape.clear()
        self._hshape.addRect(self._brect)
        self._hshapef.clear()
        self._hshapef.addRect(self._brectf)
        self.updateKeypoints()
        self.updateAnchor()

    def getMenuItems(self : Self) -> list[str]:
        return ["Appearance..."]

    def setPos(self : Self, pos : QPointF) -> None:
        self._pos = pos
        super().setPos(pos - self._anchor_offset)

    def pos(self : Self) -> QPointF:
        return self._pos

    def setPlainText(self, text: str) -> None:
        super().setPlainText(text)
        self.onSizeChange()

    def setEditable(self, editable: bool) -> None:
        self.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextEditable if editable else
            Qt.TextInteractionFlag.NoTextInteraction
        )

    def boundingRect(self : Self) -> QRectF:
        return self._brectf if self.hasFocus() else self._brect

    def shape(self : Self) -> QPainterPath:
        return self._hshapef if self.hasFocus() else self._hshape

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

    def moveKeyPoint(self : Self, kp : KPLoc, delta : QPointF) -> None:
        """Move the entire Text when any keypoint is dragged."""
        self.setPos(self.pos() + delta)

    @classmethod
    def createOrUpdate(
        cls    : Self,
        text   : Optional[str]     = None,
        pos    : Optional[QPointF] = None,
        anchor : Optional[KPLoc]      = None,
        *,
        inst   : Optional[Self] = None
    ) -> "BaseTextBlock":
        inst = cls() if inst is None else inst
        if text is not None:
            inst.setPlainText(text)
        if pos is not None:
            inst.setPos(pos)
        if anchor is not None:
            inst.setAnchorLoc(anchor)
        return inst

    def clone(self : Self) -> Self:
        clone = super().clone()
        clone.setPlainText(self.toPlainText())
        clone.setAnchorLoc(self.getAnchorLoc())
        clone.setPos(self.pos())
        return clone

class cmdPlaceBaseTextBlock(cmdPlaceElement):
    pass

