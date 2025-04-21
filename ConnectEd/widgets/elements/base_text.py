__all__ = ["BaseText"]

from typing import Self, Optional

from PyQt6.QtCore    import Qt, QPointF, QRectF, QSizeF
from PyQt6.QtWidgets import QGraphicsTextItem, QStyleOptionGraphicsItem, QWidget
from PyQt6.QtGui     import QPainter, QPainterPath, QUndoCommand, \
                            QKeyEvent, QFocusEvent

from . import Element, KeyPoint, PenSpec, BrushSpec, TextSpec, cmdPlaceElement

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


class BaseText(QGraphicsTextItem, Element):
    """Base class for text items."""
    XML_ATTRIBUTES = {
        "text"       : ( "str"       , lambda self, value: self.setText      (value) , lambda self: self.getText      () ),
        "pos"        : ( "QPointF"   , lambda self, value: self.setPos       (value) , lambda self: self.getPos       () ),
        "anchor"     : ( "KeyPoint"  , lambda self, value: self.setAnchor    (value) , lambda self: self.getAnchor    () ),
        "pen_spec"   : ( "PenSpec"   , lambda self, value: self.setPenSpec   (value) , lambda self: self.getPenSpec   () ),
        "brush_spec" : ( "BrushSpec" , lambda self, value: self.setBrushSpec (value) , lambda self: self.getBrushSpec () ),
        "text_spec"  : ( "TextSpec"  , lambda self, value: self.setTextSpec  (value) , lambda self: self.getTextSpec  () )
    }

    anchor : KeyPoint

    def __init__(
        self   : Self,
        text   : str = "<BaseText:unspecified text>",
        pos    : QPointF = QPointF(0, 0),
        anchor : KeyPoint = KeyPoint.TOP_LEFT
    ) -> None:
        QGraphicsTextItem.__init__(self, text)
        Element.__init__(self, False, False, True)
        self.setPos(pos)
        self.setZValue(self.Z)
        self.setAnchor(anchor)
        self.setTextSpec()
        self.setEditable(False)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable , True)
        self.setFlag(self.GraphicsItemFlag.ItemIsFocusable  , True)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.clearFocus()  # Trigger focusOutEvent to finish editing
            event.accept()
        else:
            super().keyPressEvent(event)

    def focusOutEvent(self, event: QFocusEvent):
        super().focusOutEvent(event)
        scene : Optional["DrawingScene"] = self.scene()
        if scene:
            scene.onTextEditingComplete(self)

    def setEditable(self, editable: bool):
        self.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextEditable if editable else
            Qt.TextInteractionFlag.NoTextInteraction
        )

    def setAnchor(self : Self, anchor : KeyPoint = KeyPoint.TOP_LEFT) -> None:
        self.anchor = anchor

    def setTextSpec(self: Self, text_spec: TextSpec = TextSpec()) -> None:
        super().setTextSpec(text_spec)
        font = self.fontFromSpec()
        if font:
            self.setFont(font)
            self.setDefaultTextColor(self.colorFromTextSpec())

    def boundingRect(self : Self) -> QRectF:
        rect = super().boundingRect()
        return QRectF(
            -rect.width() * self.anchor.value.h,
            -rect.height() * self.anchor.value.v,
            rect.width(), rect.height()
        )

    def shape(self : Self) -> QPainterPath:
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path

class cmdPlaceBaseText(cmdPlaceElement):
    element    : BaseText
    text       : str
    pos        : QPointF
    anchor     : KeyPoint

    def __init__(
        self    : Self,
        scene   : Optional["DrawingScene"] = None,
        element : Optional[BaseText] = None,
        text    : str = "",
        pos     : QPointF = QPointF(0, 0),
        anchor  : KeyPoint = KeyPoint.TOP_LEFT,
        wip     : bool = False
    ):
        super().__init__(scene, element, False, False, True, wip)
        self.text   = text
        self.pos    = pos
        self.anchor = anchor
        self.element.setAnchor(self.anchor)
        self.element.setPos(self.pos)

    def mergeWith(self : Self, other: QUndoCommand) -> bool:
        if not super().mergeWith(other):
            return False
        self.text       = other.text
        self.pos        = other.pos
        self.anchor     = other.anchor
        self.element.setPlainText(self.text)
        self.element.setAnchor(self.anchor)
        self.element.setPos(self.pos)
        return True

    def redo(self : Self):
        super().redo()
        self.element.setPlainText(self.text)
        self.element.setEditable(self.wip)
