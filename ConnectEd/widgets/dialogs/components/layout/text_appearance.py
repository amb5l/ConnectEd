from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel
from PyQt6.QtGui     import QFont, QColor

from .....core.check import checked
from .....core.types import NoChange, NO_CHANGE

from ..combo.color       import ColorComboBox
from ..combo.font_family import FontFamilyComboBox
from ..combo.font_size   import FontSizeComboBox
from ..combo.font_bool   import FontBoolComboBox


class TextAppearanceLayout(QVBoxLayout):
    _initial_color     : QColor | None | NoChange
    _initial_font      : str    | None | NoChange
    _initial_size      : float  | None | NoChange
    _initial_bold      : bool   | None | NoChange
    _initial_italic    : bool   | None | NoChange
    _initial_underline : bool   | None | NoChange
    _default_color     : QColor
    _default_font      : str
    _default_size      : float
    _default_bold      : bool
    _default_italic    : bool
    _default_underline : bool
    _options_layout    : QGridLayout
    _color_label       : QLabel
    _color_combo       : ColorComboBox
    _font_label        : QLabel
    _font_combo        : FontFamilyComboBox
    _size_label        : QLabel
    _size_combo        : FontSizeComboBox
    _bold_label        : QLabel
    _bold_combo        : FontBoolComboBox
    _italic_label      : QLabel
    _italic_combo      : FontBoolComboBox
    _underline_label   : QLabel
    _underline_combo   : FontBoolComboBox

    @checked
    def __init__(
        self              : Self,
        initial_color     : QColor | None | NoChange,
        initial_font      : str    | None | NoChange,
        initial_size      : float  | None | NoChange,
        initial_bold      : bool   | None | NoChange,
        initial_italic    : bool   | None | NoChange,
        initial_underline : bool   | None | NoChange,
        default_color     : QColor,
        default_font      : str,
        default_size      : float,
        default_bold      : bool,
        default_italic    : bool,
        default_underline : bool,
        parent            : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._initial_color     = initial_color
        self._initial_font      = initial_font
        self._initial_size      = initial_size
        self._initial_bold      = initial_bold
        self._initial_italic    = initial_italic
        self._initial_underline = initial_underline
        self._default_color     = default_color
        self._default_font      = default_font
        self._default_size      = default_size
        self._default_bold      = default_bold
        self._default_italic    = default_italic
        self._default_underline = default_underline
        self._options_layout = QGridLayout()
        self._color_label = QLabel("Color:")
        self._options_layout.addWidget(self._color_label, 0, 0)
        self._color_combo = ColorComboBox(initial_color, default_color)
        self._options_layout.addWidget(self._color_combo, 0, 1)
        self._font_label = QLabel("Font:")
        self._options_layout.addWidget(self._font_label, 1, 0)
        self._font_combo = FontFamilyComboBox(initial_font, default_font)
        self._options_layout.addWidget(self._font_combo, 1, 1)
        self._size_label = QLabel("Size:")
        self._options_layout.addWidget(self._size_label, 2, 0)
        self._size_combo = FontSizeComboBox(initial_size, default_size)
        self._options_layout.addWidget(self._size_combo, 2, 1)
        self._bold_label = QLabel("Bold:")
        self._options_layout.addWidget(self._bold_label, 3, 0)
        self._bold_combo = FontBoolComboBox(initial_bold, default_bold)
        self._options_layout.addWidget(self._bold_combo, 3, 1)
        self._italic_label = QLabel("Italic:")
        self._options_layout.addWidget(self._italic_label, 4, 0)
        self._italic_combo = FontBoolComboBox(initial_italic, default_italic)
        self._options_layout.addWidget(self._italic_combo, 4, 1)
        self._underline_label = QLabel("Underline:")
        self._options_layout.addWidget(self._underline_label, 5, 0)
        self._underline_combo = FontBoolComboBox(initial_underline, default_underline)
        self._options_layout.addWidget(self._underline_combo, 5, 1)
        self.addLayout(self._options_layout)

    @checked
    def getColor(self : Self) -> QColor | NoChange:
        return self._color_combo.value()

    @checked
    def getFont(self : Self) -> str | NoChange:
        return self._font_combo.value()

    @checked
    def getSize(self : Self) -> float | NoChange:
        return self._size_combo.value()

    @checked
    def getBold(self : Self) -> bool | NoChange:
        return self._bold_combo.value()

    @checked
    def getItalic(self : Self) -> bool | NoChange:
        return self._italic_combo.value()

    @checked
    def getUnderline(self : Self) -> bool | NoChange:
        return self._underline_combo.value()


class TextAppearancePreviewLayout(TextAppearanceLayout):
    _preview : QLabel

    @checked
    def __init__(
        self              : Self,
        initial_color     : QColor | None | NoChange,
        initial_font      : str    | None | NoChange,
        initial_size      : float  | None | NoChange,
        initial_bold      : bool   | None | NoChange,
        initial_italic    : bool   | None | NoChange,
        initial_underline : bool   | None | NoChange,
        default_color     : QColor,
        default_font      : str,
        default_size      : float,
        default_bold      : bool,
        default_italic    : bool,
        default_underline : bool,
        parent            : QWidget | None = None
    ) -> None:
        super().__init__(
            initial_color,
            initial_font,
            initial_size,
            initial_bold,
            initial_italic,
            initial_underline,
            default_color,
            default_font,
            default_size,
            default_bold,
            default_italic,
            default_underline,
            parent
        )
        self._preview = QLabel("Sample Text")
        self._preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview.setMinimumHeight(40)
        self._updatePreview()
        self.addWidget(self._preview)
        self._font_combo.activated.connect(self._updatePreview)
        self._bold_combo.activated.connect(self._updatePreview)
        self._italic_combo.activated.connect(self._updatePreview)
        self._underline_combo.activated.connect(self._updatePreview)

    def _updatePreview(self : Self) -> None:
        if isinstance(font := self._font_combo.value(), NoChange):
            font = self._initial_font
        if font is None:
            font = self._default_font
        if isinstance(bold := self._bold_combo.value(), NoChange):
            bold = self._initial_bold
        if bold is None:
            bold = self._default_bold
        if isinstance(italic := self._italic_combo.value(), NoChange):
            italic = self._initial_italic
        if italic is None:
            italic = self._default_italic
        if isinstance(underline := self._underline_combo.value(), NoChange):
            underline = self._initial_underline
        if underline is None:
            underline = self._default_underline
        if isinstance(font, NoChange) \
        or isinstance(bold, NoChange) \
        or isinstance(italic, NoChange) \
        or isinstance(underline, NoChange):
            self._preview.setText("") # options are ambiguous
            return
        qfont = QFont()
        qfont.setFamily(font)
        qfont.setPointSizeF(24.0) # TODO scale with dialog, or use settings?
        qfont.setBold(bold)
        qfont.setItalic(italic)
        qfont.setUnderline(underline)
        self._preview.setFont(qfont)
        self._preview.setText("Sample Text")
