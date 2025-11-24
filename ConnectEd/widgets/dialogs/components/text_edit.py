from typing import Self

from PyQt6.QtWidgets import QTextEdit


class TextEdit(QTextEdit):
    def text(self : Self) -> str:
        return self.toPlainText()
