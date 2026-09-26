from __future__ import annotations

from typing import Self

from PyQt6.QtGui import QColor, QFont

from ...core.check import checked


class Quill:
    _color : QColor
    _qfont : QFont

    @checked
    def __init__(
        self      : Self,
        a0        : Quill | QColor | None = None,
        font      : str            | None = None,
        size      : float          | None = None,
        bold      : bool           | None = None,
        italic    : bool           | None = None,
        underline : bool           | None = None,
    ) -> None:
        if isinstance(a0, Quill):
            if any(v is not None for v in (font, size, bold, italic, underline)):
                raise TypeError("Cannot mix a Quill copy with component arguments")
            self._color = QColor(a0._color)
            self._qfont  = QFont(a0._qfont)
            return
        self._color = QColor(a0)
        self._qfont  = QFont()
        self._qfont.setFamily(font if font is not None else QFont().family())
        self._qfont.setPointSizeF(size if size is not None else QFont().pointSizeF())
        self._qfont.setBold(bold if bold is not None else False)
        self._qfont.setItalic(italic if italic is not None else False)
        self._qfont.setUnderline(underline if underline is not None else False)

    def color(self : Self) -> QColor:
        return self._color

    def setColor(self : Self, color: QColor) -> None:
        self._color = color

    def font(self : Self) -> str:
        return self._qfont.family()

    def setFont(self : Self, font: str) -> None:
        self._qfont.setFamily(font)

    def size(self : Self) -> float:
        return self._qfont.pointSizeF()

    def setSize(self : Self, size: float) -> None:
        self._qfont.setPointSizeF(size)

    def bold(self : Self) -> bool:
        return self._qfont.bold()

    def setBold(self : Self, bold: bool) -> None:
        self._qfont.setBold(bold)

    def italic(self : Self) -> bool:
        return self._qfont.italic()

    def setItalic(self : Self, italic: bool) -> None:
        self._qfont.setItalic(italic)

    def underline(self : Self) -> bool:
        return self._qfont.underline()

    def setUnderline(self : Self, underline: bool) -> None:
        self._qfont.setUnderline(underline)

    def qFont(self : Self) -> QFont:
        return self._qfont
