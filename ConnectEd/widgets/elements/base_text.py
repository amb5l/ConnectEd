__all__ = ["BaseText"]

from typing import Self, Optional, Any

from PyQt6.QtCore    import Qt, QPointF, QRectF
from PyQt6.QtWidgets import QWidget, QStyleOptionGraphicsItem, QStyle
from PyQt6.QtGui     import QPainter, QPainterPath, QUndoCommand, QPen, \
                            QKeyEvent, QFocusEvent, QColor

from . import QGraphicsTextItemCustomized, Element, AnchorGrip, \
              KeyPoint, TextSpec, cmdPlaceElement

from ... import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


class BaseText(QGraphicsTextItemCustomized, Element):
    """Base class for text items."""
    XML_ATTRIBUTES = {
        "text"       : ( "str"       , lambda self, value: self.setText      (value) , lambda self: self.getText      () ),
        "pos"        : ( "QPointF"   , lambda self, value: self.setPos       (value) , lambda self: self.getPos       () ),
        "anchor"     : ( "KeyPoint"  , lambda self, value: self.setAnchor    (value) , lambda self: self.getAnchor    () ),
        "pen_spec"   : ( "PenSpec"   , lambda self, value: self.setPenSpec   (value) , lambda self: self.getPenSpec   () ),
        "brush_spec" : ( "BrushSpec" , lambda self, value: self.setBrushSpec (value) , lambda self: self.getBrushSpec () ),
        "text_spec"  : ( "TextSpec"  , lambda self, value: self.setTextSpec  (value) , lambda self: self.getTextSpec  () )
    }

    grips  : dict[KeyPoint, AnchorGrip]
    anchor : KeyPoint

    def __init__(
        self   : Self,
        text   : str = "<BaseText:unspecified text>",
        pos    : QPointF = QPointF(0, 0),
        anchor : KeyPoint = KeyPoint.TOP_LEFT
    ) -> None:
        QGraphicsTextItemCustomized.__init__(self, text)
        QGraphicsTextItemCustomized.document(self).setDocumentMargin(0)
        Element.__init__(self, False, False, True)
        self.grips = {p: AnchorGrip(self, p) for p in KeyPoint}
        self.setPos(pos)
        self.setZValue(self.Z)
        self.setAnchor(anchor)
        self.setTextSpec()
        self.setEditable(False)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable , True)
        self.setFlag(self.GraphicsItemFlag.ItemIsFocusable  , True)
        self.updateGripsPosition()
        self.updateGripsVisibility()
        self.updateGripsZValue()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.clearFocus()
            event.accept()
        else:
            super().keyPressEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        super().focusOutEvent(event)
        scene : Optional["DrawingScene"] = self.scene()
        if scene:
            scene.onTextEditingComplete(self)

    def setPos(self, pos: QPointF) -> None:
        super().setPos(pos)
        self.updateGripsPosition()

    def setPlainText(self, text: str) -> None:
        super().setPlainText(text)
        self.updateGripsPosition()

    def setEditable(self, editable: bool) -> None:
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

    def updateGripsPosition(self : Self) -> None:
        for kp in self.grips.keys():
            self.grips[kp].setPos(
                kp.value.h * super().boundingRect().width(),
                kp.value.v * super().boundingRect().height()
            )

    def updateGripsVisibility(self : Self) -> None:
        for grip in self.grips.values():
            grip.setVisible(
                self.isSelected() and len(self.scene().selectedItems()) == 1
            )

    def updateGripsZValue(self : Self) -> None:
        for grip in self.grips.values():
            grip.setZValue(self.zValue() + grip.Z_DELTA)

    def boundingRect(self : Self) -> QRectF:
        rect = super().boundingRect()
        adjusted =QRectF(
            -rect.width() * self.anchor.value.h,
            -rect.height() * self.anchor.value.v,
            rect.width(), rect.height()
        )
        if self.hasFocus():
            # compensate for focus rect inset
            adjusted.adjust(-0.5, -0.5, 0.5, 0.5)
        return adjusted

    def shape(self : Self) -> QPainterPath:
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path

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
        if self.isSelected():
            # override text color
            theme = hub.settings.theme.selected.text
            c = self.defaultTextColor()
            self.setDefaultTextColor(theme)
        super().paint(painter, option, widget)
        if self.isSelected():
            prefs = hub.settings.prefs.display.elements.selected.line
            painter.setPen(QPen(theme, prefs.width, prefs.style))
            painter.drawRect(self.boundingRect())
        if c:
            self.setDefaultTextColor(c)

    def itemChange(
        self   : Self,
        change : QGraphicsTextItemCustomized.GraphicsItemChange,
        value  : Any
    ) -> None:
        if change == self.GraphicsItemChange.ItemSelectedHasChanged:
            self.updateGripsVisibility()
        return QGraphicsTextItemCustomized.itemChange(self, change, value)

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
    ) -> None:
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

    def redo(self : Self) -> None:
        super().redo()
        self.element.setPlainText(self.text)
        self.element.setEditable(self.wip)
