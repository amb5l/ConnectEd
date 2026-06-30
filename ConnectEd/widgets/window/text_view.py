import logging

from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QPlainTextEdit, QDockWidget, QVBoxLayout
from PyQt6.QtGui     import QTextOption, QContextMenuEvent, QWheelEvent

from ...app import logger, settings

from ...core.check import checked

from ..action import Action

from .find_bar import FindBar


class TextView(QPlainTextEdit):
    _find_bar : FindBar | None
    _actions  : dict[str, Action]

    @checked
    def __init__(
        self     : Self,
        parent   : QWidget,
        filename : str | None = None
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
        vertical_scroll_bar = self.verticalScrollBar()
        if vertical_scroll_bar is None:
            raise RuntimeError("No vertical scroll bar")
        vertical_scroll_bar.setValue(vertical_scroll_bar.maximum())
        self._find_bar = None
        self._actions = {}
        self._actions["showFindBar"] = Action(self, "Find Bar")
        self._actions["showFindBar"].setCheckable(True)
        self._actions["showFindBar"].setChecked(False)
        self._actions["showFindBar"].triggered.connect(self.showFindBar)
        self.addAction(self._actions["showFindBar"])

    def setFindBar(self : Self, find_bar : FindBar) -> None:
        self._find_bar = find_bar

    def wheelEvent(self : Self, e : QWheelEvent | None) -> None:
        if e is None:
            logger().warning("No event")
            return
        """Handle mouse wheel events to adjust font size when Ctrl is pressed."""
        modifiers = e.modifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            font = self.font()
            current_size = font.pointSize()
            delta = e.angleDelta().y()
            if delta > 0:
                font.setPointSizeF(min(current_size + 1, 24)) # TODO: max from settings
            elif delta < 0:
                font.setPointSizeF(max(current_size - 1, 6))  # TODO: min from settings
            self.setFont(font)
            e.accept()  # Prevent default scrolling when adjusting font
        else:
            super().wheelEvent(e)  # Default scrolling behavior

    def contextMenuEvent(self : Self, e : QContextMenuEvent | None) -> None:
        if e is None:
            logger().warning("No event")
            return
        menu = self.createStandardContextMenu()
        if menu is None:
            raise RuntimeError("No menu")
        menu.addSeparator()
        menu.addAction(self._actions["showFindBar"])
        menu.exec(e.globalPos())

    def showFindBar(self : Self, checked : bool) -> None:
        if self._find_bar:
            self._find_bar.setVisible(checked)
            if checked:
                self._find_bar.find_combo.setFocus()
                line_edit = self._find_bar.find_combo.lineEdit()
                if line_edit is None:
                    raise RuntimeError("No line edit")
                line_edit.selectAll()

class TextViewDockWidget(QDockWidget):
    WINDOW_TITLE = "Text Viewer"
    _main_widget  : QWidget
    _text_view    : TextView
    _find_bar     : FindBar

    @checked
    def __init__(
        self     : Self,
        parent   : QWidget | None = None,
        filename : str | None = None
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(self.WINDOW_TITLE)
        self._text_view = TextView(self, filename)
        self._find_bar = FindBar(self, self._text_view)
        self._text_view.setFindBar(self._find_bar)
        self._main_widget = QWidget()
        layout = QVBoxLayout(self._main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._find_bar)
        layout.addWidget(self._text_view)
        self._main_widget.setLayout(layout)
        self.setWidget(self._main_widget)
        self._find_bar.hide()
