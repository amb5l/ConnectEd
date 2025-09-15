import logging

from types  import SimpleNamespace
from typing import Self, Optional

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QPlainTextEdit, QDockWidget, QVBoxLayout
from PyQt6.QtGui     import QTextOption, QAction, QContextMenuEvent, QWheelEvent

from ...app import logger, settings

from .find_bar import FindBar


class TextView(QPlainTextEdit):
    actions  : SimpleNamespace
    find_bar : Optional[FindBar] = None
    handler  : Optional[logging.Handler] = None

    def __init__(
        self     : Self,
        parent   : QWidget,
        filename : Optional[str] = None
    ) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.setUndoRedoEnabled(False)
        self.setWordWrapMode(QTextOption.WrapMode.NoWrap)
        font = self.font()
        font.setFamily("Liberation Mono")  # TODO: get from settings
        font.setPointSizeF(settings().get("display/font_size"))
        self.setFont(font)
        if filename:
            with open(filename, "r") as f:
                content = f.read()
                if content.endswith("\n"):
                    content = content[:-1]
            self.setPlainText(content)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        self.actions = SimpleNamespace()
        self.actions.showFindBar = QAction("Find Bar", self)
        self.actions.showFindBar.setCheckable(True)
        self.actions.showFindBar.setChecked(False)
        self.actions.showFindBar.triggered.connect(self.showFindBar)
        self.addAction(self.actions.showFindBar)
        self.handler = None

    def setFindBar(self : Self, find_bar : FindBar) -> None:
        self.find_bar = find_bar

    def wheelEvent(self : Self, event : QWheelEvent) -> None:
        """Handle mouse wheel events to adjust font size when Ctrl is pressed."""
        modifiers = event.modifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            font = self.font()
            current_size = font.pointSize()
            delta = event.angleDelta().y()
            if delta > 0:
                font.setPointSizeF(min(current_size + 1, 24)) # TODO: max from settings
            elif delta < 0:
                font.setPointSizeF(max(current_size - 1, 6))  # TODO: min from settings
            self.setFont(font)
            event.accept()  # Prevent default scrolling when adjusting font
        else:
            super().wheelEvent(event)  # Default scrolling behavior

    def contextMenuEvent(self : Self, event : QContextMenuEvent) -> None:
        menu = self.createStandardContextMenu()
        menu.addSeparator()
        menu.addAction(self.actions.showFindBar)
        menu.exec(event.globalPos())

    def showFindBar(self : Self, checked : bool) -> None:
        if self.find_bar:
            self.find_bar.setVisible(checked)
            if checked:
                self.find_bar.find_combo.setFocus()
                self.find_bar.find_combo.lineEdit().selectAll()

    def __del__(self : Self) -> None:
        if hasattr(self, "handler") and self.handler:
            try:
                logger().removeHandler(self.handler)
            except:
                pass

class TextViewDockWidget(QDockWidget):
    WINDOW_TITLE = "Text Viewer"
    main_widget  : QWidget
    text_view    : TextView
    find_bar     : FindBar

    def __init__(
        self     : Self,
        parent   : Optional[QWidget] = None,
        filename : Optional[str] = None
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.text_view = TextView(self, filename)
        self.find_bar = FindBar(self, self.text_view)
        self.text_view.setFindBar(self.find_bar)
        self.main_widget = QWidget()
        layout = QVBoxLayout(self.main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.find_bar)
        layout.addWidget(self.text_view)
        self.main_widget.setLayout(layout)
        self.setWidget(self.main_widget)
        self.find_bar.hide()
