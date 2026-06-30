from __future__ import annotations

from ...core.check import checked
from PyQt6.QtGui import QColor, QFont


class Quill:
    _color : QColor
    _qfont : QFont

    @checked
    def __init__(
        self,
        color     : QColor | Quill,
        font      : str   | None = None,
        size      : float | None = None,
        bold      : bool  | None = None,
        italic    : bool  | None = None,
        underline : bool  | None = None,
    ) -> None:
        if isinstance(color, Quill):
            if any(v is not None for v in (font, size, bold, italic, underline)):
                raise TypeError("Cannot mix a Quill copy with component arguments")
            self._color = QColor(color._color)
            self._qfont  = QFont(color._qfont)
            return
        self._color = QColor(color)
        self._qfont  = QFont()
        self._qfont.setFamily(font if font is not None else QFont().family())
        self._qfont.setPointSizeF(size if size is not None else QFont().pointSizeF())
        self._qfont.setBold(bold if bold is not None else False)
        self._qfont.setItalic(italic if italic is not None else False)
        self._qfont.setUnderline(underline if underline is not None else False)

    def color(self) -> QColor:
        return self._color

    def setColor(self, color: QColor) -> None:
        self._color = color

    def font(self) -> str:
        return self._qfont.family()

    def setFont(self, font: str) -> None:
        self._qfont.setFamily(font)

    def size(self) -> float:
        return self._qfont.pointSizeF()

    def setSize(self, size: float) -> None:
        self._qfont.setPointSizeF(size)

    def bold(self) -> bool:
        return self._qfont.bold()

    def setBold(self, bold: bool) -> None:
        self._qfont.setBold(bold)

    def italic(self) -> bool:
        return self._qfont.italic()

    def setItalic(self, italic: bool) -> None:
        self._qfont.setItalic(italic)

    def underline(self) -> bool:
        return self._qfont.underline()

    def setUnderline(self, underline: bool) -> None:
        self._qfont.setUnderline(underline)

    def qFont(self) -> QFont:
        return self._qfont
