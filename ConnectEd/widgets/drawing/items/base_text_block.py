__all__ = ["BaseTextBlock"]

from typing import Self, Optional

from PyQt6.QtCore    import Qt, QPointF, QRectF
from PyQt6.QtWidgets import QWidget, QStyleOptionGraphicsItem, QStyle, \
                            QGraphicsTextItem
from PyQt6.QtGui     import QColor, QPainter, QPainterPath, \
                            QKeyEvent, QFocusEvent, QTextCursor

from ..properties import PropertySpec, PropertiesMixin

from . import APType, \
              ElementMixin, \
              ElementBoundShapeMixin, \
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
    from .. import DrawingScene


class BaseTextBlock(
    ElementMixin,
    ElementBoundShapeMixin,
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
    QGraphicsTextItem
):
    # class variables
    _AP_TYPES = { k : APType.Mover \
            for k in ElementRectAnchorPointsMixin._ANCHOR_POINTS.keys() }
    _PROPERTY_SPECS = \
        ElementOriginMixin._PROPERTY_SPECS_ORIGIN | \
        ElementPosMixin._PROPERTY_SPECS_POS | \
        {
            "Text" : PropertySpec(
                type_name = "str",
                getter    = lambda self: self.toPlainText(),
                setter    = lambda self, value: self.setPlainText(value)
            )
        } | \
        ElementQuillMixin._PROPERTY_SPECS_QUILL

    # instance attributes
    _rect    : QRectF        # border rectangle (for keypoints)
    _brectf  : QRectF        # bounding rect when has focus
    _hshapef : QPainterPath  # hit detect shape when has focus

    def __init__(self : Self, bare : bool = False) -> None:
        QGraphicsTextItem.__init__(self)
        self.initElement(bare=bare)
        self.setEditable(False)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable , True)
        self.setFlag(self.GraphicsItemFlag.ItemIsFocusable, True)
        self._brectf = QRectF()
        self._hshapef = QPainterPath()
        self.onGeometryChange()
        self.updateHandlesVisibility()

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
            QGraphicsTextItem.keyPressEvent(self, event)
        self.onGeometryChange()  # text change means size change

    def focusOutEvent(self, event: QFocusEvent) -> None:
        QGraphicsTextItem.focusOutEvent(self, event)
        scene : Optional["DrawingScene"] = self.scene()
        if scene:
            scene.onTextEditingComplete(self)

    def onGeometryChange(self : Self) -> None:
        self.prepareGeometryChange()
        self._brect = self._rect = QGraphicsTextItem.boundingRect(self)
        self._brectf = self._brect.adjusted(-0.5, -0.5, 0.5, 0.5)
        self._hshape.clear()
        self._hshape.addRect(self._brect)
        self._hshapef.clear()
        self._hshapef.addRect(self._brectf)
        self.updateKeypoints()
        self.updateOrigin()

    def getMenuItems(self : Self) -> list[str]:
        return ["Appearance..."]

    def setPlainText(self, text: str) -> None:
        QGraphicsTextItem.setPlainText(self, text)
        self.onGeometryChange()

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
        QGraphicsTextItem.paint(self, painter, option, widget)
        if self.isSelected():
            painter.setPen(self.outline.pen)
            painter.drawRect(self.boundingRect())

    def moveAnchorPointBy(self : Self, _ : str, delta : QPointF) -> None:
        """Move the entire Text when any keypoint is dragged."""
        self.setPos(self.pos() + delta)

    @classmethod
    def createOrUpdate(
        cls    : Self,
        text   : Optional[str]     = None,
        pos    : Optional[QPointF] = None,
        anchor : Optional[str]     = None,
        *,
        inst   : Optional[Self] = None
    ) -> "BaseTextBlock":
        inst = cls() if inst is None else inst
        if text is not None:
            inst.setPlainText(text)
        if pos is not None:
            inst.setPos(pos)
        if anchor is not None:
            inst.setOrigin(anchor)
        return inst
