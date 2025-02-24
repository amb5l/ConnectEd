import logging

from PyQt6.QtWidgets import QWidget, QPlainTextEdit
from PyQt6.QtGui     import QTextOption, QAction, QKeySequence

from ..core    import logger
from .find_bar import FindBar


class TextView(QPlainTextEdit):
    find_bar : FindBar | None
    handler  : logging.Handler | None

    def __init__(
        self     : 'TextView',
        parent   : QWidget,
        filename : str | None = None
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

    def contextMenuEvent(self, event):
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

    def __del__(self):
        if hasattr(self, 'handler') and self.handler:
            try:
                logger.removeHandler(self.handler)
            except:
                pass
