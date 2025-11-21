from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui  import QFocusEvent, QKeyEvent, QMouseEvent, QWheelEvent

from ....app import model, logger

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Navigator


class NavigatorOverridesMixin:

    def focusInEvent(self : "Navigator", event : QFocusEvent) -> None:
        self._focus_in = True
        super().focusInEvent(event)

    def keyPressEvent(self : "Navigator", event : QKeyEvent) -> None:
        if event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            if len(self.selectedIndexes()) == 1:
                index = self.selectedIndexes()[0]
                if index.isValid():
                    self._doubleClickOrEnter(model().itemFromIndex(index))
                    event.accept()

    def mousePressEvent(self : "Navigator", event : QMouseEvent) -> None:
        """Handle mouse press to deselect items when clicking in empty space."""
        index = self.indexAt(event.pos())
        if not index.isValid() and event.button() in \
            [Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton]:
            if self._focus_in:
                self._focus_in = False
            else:
                self.clearSelection()
                self.setCurrentIndex(model().index(-1, -1))  # invalid index
                if event.button() == Qt.MouseButton.LeftButton:
                    event.accept()
                    return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self : "Navigator", event : QMouseEvent) -> None:
        """Handle double-click."""
        if event.button() == Qt.MouseButton.LeftButton:
            index = self.indexAt(event.pos())
            if index.isValid():
                self._doubleClickOrEnter(model().itemFromIndex(index))
                event.accept()
                return
        super().mouseDoubleClickEvent(event)

    def wheelEvent(self : "Navigator", event : QWheelEvent) -> None:
        """Handle mouse wheel events to adjust font size when Ctrl is pressed."""
        modifiers = event.modifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.increaseFontSize()
            elif delta < 0:
                self.decreaseFontSize()
            event.accept()
            return
        super().wheelEvent(event)

    def showContextMenu(self : "Navigator", pos : QPoint) -> None:
        index = self.indexAt(pos)
        if index.isValid():
            self.node = model().itemFromIndex(index)
            node_kind = type(self.node).__name__
            if node_kind not in self.menus:
                logger().error(f"Unknown node type: {node_kind}")
                return
            menu = self.menus[node_kind]
        else:
            menu = self.menus[None]
        menu.exec(self.viewport().mapToGlobal(pos))
