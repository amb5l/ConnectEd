import logging
from typing import Optional

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QPlainTextEdit
from PyQt6.QtGui     import QTextOption, QAction, QContextMenuEvent, QWheelEvent

from ..core    import logger
from .find_bar import FindBar


class TextView(QPlainTextEdit):
    find_bar : Optional[FindBar] = None
    handler  : Optional[logging.Handler] = None

    def __init__(
        self     : 'TextView',
        parent   : QWidget,
        filename : Optional[str] = None
    ) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.setUndoRedoEnabled(False)
        self.setWordWrapMode(QTextOption.WrapMode.NoWrap)
        font = self.font()
        font.setFamily('Intel One Mono')
        font.setPointSize(10)
        self.setFont(font)
        if filename:
            with open(filename, 'r') as f:
                content = f.read()
                if content.endswith('\n'):
                    content = content[:-1]
            self.setPlainText(content)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        self.find_bar_action = QAction('Find Bar', self)
        self.find_bar_action.setCheckable(True)
        self.find_bar_action.setChecked(False)
        self.find_bar_action.triggered.connect(self.slotFindBar)
        self.addAction(self.find_bar_action)
        self.handler = None

    def setFindBar(self, find_bar : FindBar) -> None:
        self.find_bar = find_bar

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Handle mouse wheel events to adjust font size when Ctrl is pressed."""
        modifiers = event.modifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            font = self.font()
            current_size = font.pointSize()
            delta = event.angleDelta().y()
            if delta > 0:
                font.setPointSize(min(current_size + 1, 24)) # TODO: max from settings
            elif delta < 0:
                font.setPointSize(max(current_size - 1, 6))  # TODO: min from settings
            self.setFont(font)
            event.accept()  # Prevent default scrolling when adjusting font
        else:
            super().wheelEvent(event)  # Default scrolling behavior

    def contextMenuEvent(self, event : QContextMenuEvent) -> None:
        menu = self.createStandardContextMenu()
        menu.addSeparator()
        menu.addAction(self.find_bar_action)
        menu.exec(event.globalPos())

    def slotFindBar(self, checked : bool) -> None:
        if self.find_bar:
            logger.debug(f"slot_find: {checked}")
            self.find_bar.setVisible(checked)
            if checked:
                self.find_bar.find_combo.setFocus()
                self.find_bar.find_combo.lineEdit().selectAll()

    def __del__(self : 'TextView') -> None:
        if hasattr(self, 'handler') and self.handler:
            try:
                logger.removeHandler(self.handler)
            except:
                pass
