__all__ = ["BaseTextBlock"]

from typing import Self, Optional, Any
from types  import SimpleNamespace

from PyQt6.QtCore    import Qt, QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsTextItem, QWidget, \
                            QStyleOptionGraphicsItem, QStyle, \
                            QMenu, QGraphicsSceneContextMenuEvent
from PyQt6.QtGui     import QPainter, QPainterPath, QUndoCommand, QPen, \
                            QKeyEvent, QFocusEvent, QColor, QAction, \
                            QTextCursor

from ...dialogs import TextFontDialog

from . import Element, KPManager, KPLoc, KPDef, cmdPlaceElement

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


class BaseTextBlock(QGraphicsTextItem, Element):
    """Base class for text items."""
    XML_ATTRS = Element.XML_ATTRS | {
        "text" : (
            "str",
            lambda self, value: self.setPlainText(value),
            lambda self: self.toPlainText()
        )
    }

    _kpm     : KPManager
    _rect    : QRectF
    _shape   : QPainterPath
    _menu    : QMenu
    _actions : SimpleNamespace

    def __init__(
        self   : Self,
        text   : str = "",
        pos    : QPointF = QPointF(0, 0),
        anchor : KPLoc = KPLoc.TOP_LEFT
    ) -> None:
        self._rect = QRectF()
        self._shape = QPainterPath()
        QGraphicsTextItem.__init__(self, text)
        Element.__init__(self, has_text=True)
        self._kpm = KPManager(
            self,
            [KPDef(k, False, False) for k in KPLoc],
            KPLoc.TOP_LEFT
        )
        self.setPos(pos)
        self.setEditable(False)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable , True)
        self.setFlag(self.GraphicsItemFlag.ItemIsFocusable  , True)
        self._menu = QMenu()
        self._actions = SimpleNamespace()
        self._actions.font = QAction("Font")
        self._actions.font.triggered.connect(self.ctxMenuFont)
        self._menu.addAction(self._actions.font)
        # edit properties
        # move
        # delete
        # assign anchor
        # link

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

    def contextMenuEvent(self : Self, event : QGraphicsSceneContextMenuEvent) -> None:
        self._menu.exec(event.screenPos())

    def setPos(self : Self, pos : QPointF) -> None:
        super().setPos(pos - self._kpm.anchor_offset)

    def pos(self : Self) -> QPointF:
        return super().pos() + self._kpm.anchor_offset

    def setPlainText(self, text: str) -> None:
        super().setPlainText(text)
        self._rect = super().boundingRect()
        self._shape.clear()
        self._shape.addRect(self._rect)
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

    KPRect = boundingRect

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
            painter.setPen(self.appearance.outline.pen)
            painter.drawRect(self.boundingRect())

    def setAnchor(self : Self, anchor : KPLoc = KPLoc.TOP_LEFT) -> None:
        self._kpm.setAnchor(anchor)

    def setKPVisible(self : Self, visible : bool) -> None:
        self._kpm.setVisible(visible)

    def ctxMenuFont(self : Self) -> None:
        s = self.appearance.text
        d = self.appearance.text.getDefaults()
        dialog = TextFontDialog(
            family    = ( s.getFamily()    , d.family    ),
            size      = ( s.getSize()      , d.size      ),
            bold      = ( s.getBold()      , d.bold      ),
            italic    = ( s.getItalic()    , d.italic    ),
            underline = ( s.getUnderline() , d.underline )
        )
        if dialog.exec():
            self.appearance.text.setFamily    ( dialog.chosen_family    )
            self.appearance.text.setSize      ( dialog.chosen_size      )
            self.appearance.text.setBold      ( dialog.chosen_bold      )
            self.appearance.text.setItalic    ( dialog.chosen_italic    )
            self.appearance.text.setUnderline ( dialog.chosen_underline )
            scene = self.scene()
            if scene:
                scene.update()

class cmdPlaceBaseTextBlock(cmdPlaceElement):
    element    : BaseTextBlock
    text       : str
    pos        : QPointF
    anchor     : KPLoc

    def __init__(
        self    : Self,
        scene   : Optional["DrawingScene"] = None,
        element : Optional[BaseTextBlock] = None,
        text    : str = "",
        pos     : QPointF = QPointF(0, 0),
        anchor  : KPLoc = KPLoc.TOP_LEFT
    ) -> None:
        super().__init__(scene, element)
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
        self.element.setPos(self.pos)
        self.element.setAnchor(self.anchor)
        self.element.setEditable(True)
