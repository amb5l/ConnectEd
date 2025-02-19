from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtGui     import QTextOption

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .main_window import MainWindow


class TextFileViewer(QPlainTextEdit):
    def __init__(
        self     : 'TextFileViewer',
        parent   : 'MainWindow',
        filename : str
    ) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.setUndoRedoEnabled(False)
        self.setWordWrapMode(QTextOption.WrapMode.NoWrap)
        font = self.font()
        font.setFamily('Courier')
        self.setFont(font)
        with open(filename, 'r') as f:
            content = f.read()
            if content.endswith('\n'):
                content = content[:-1]
            self.setPlainText(content)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        # scroll down so the the end of the file is visible
        #self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

