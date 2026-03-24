from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel
from PyQt6.QtGui     import QFont, QColor

from .....core.check import checked
from .....core.types import Default, DEFAULT, NoChange, NO_CHANGE, \
                            Color, FontFamily, FontSize, FontBool

from ..combo.color       import ColorComboBox
from ..combo.font_family import FontFamilyComboBox
from ..combo.font_size   import FontSizeComboBox
from ..combo.font_bool   import FontBoolComboBox


class TextAppearanceLayout(QVBoxLayout):
    _initial_color     : Color      | NoChange
    _initial_family    : FontFamily | NoChange
    _initial_size      : FontSize   | NoChange
    _initial_bold      : FontBool   | NoChange
    _initial_italic    : FontBool   | NoChange
    _initial_underline : FontBool   | NoChange
    _default_color     : QColor
    _default_family    : str
    _default_size      : float
    _default_bold      : bool
    _default_italic    : bool
    _default_underline : bool
    _options_layout     : QGridLayout
    _color_label        : QLabel
    _color_combo        : ColorComboBox
    _family_label       : QLabel
    _family_combo       : FontFamilyComboBox
    _size_label         : QLabel
    _size_combo         : FontSizeComboBox
    _bold_label         : QLabel
    _bold_combo         : FontBoolComboBox
    _italic_label       : QLabel
    _italic_combo       : FontBoolComboBox
    _underline_label    : QLabel
    _underline_combo    : FontBoolComboBox

    @checked
    def __init__(
        self              : Self,
        initial_color     : Color      | NoChange,
        initial_family    : FontFamily | NoChange,
        initial_size      : FontSize   | NoChange,
        initial_bold      : FontBool   | NoChange,
        initial_italic    : FontBool   | NoChange,
        initial_underline : FontBool   | NoChange,
        default_color     : QColor,
        default_family    : str,
        default_size      : float,
        default_bold      : bool,
        default_italic    : bool,
        default_underline : bool,
        parent            : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._initial_color     = initial_color
        self._initial_family    = initial_family
        self._initial_size      = initial_size
        self._initial_bold      = initial_bold
        self._initial_italic    = initial_italic
        self._initial_underline = initial_underline
        self._default_color     = default_color
        self._default_family    = default_family
        self._default_size      = default_size
        self._default_bold      = default_bold
        self._default_italic    = default_italic
        self._default_underline = default_underline
        self._options_layout = QGridLayout()
        self._color_label = QLabel("Color:")
        self._options_layout.addWidget(self._color_label, 0, 0)
        self._color_combo = ColorComboBox(initial_color, default_color)
        self._options_layout.addWidget(self._color_combo, 0, 1)
        self._family_label = QLabel("Font:")
        self._options_layout.addWidget(self._family_label, 1, 0)
        self._family_combo = FontFamilyComboBox(initial_family, default_family)
        self._options_layout.addWidget(self._family_combo, 1, 1)
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
    def getColor(self : Self) -> Color | NoChange:
        return self._color_combo.value()

    @checked
    def getFamily(self : Self) -> FontFamily | NoChange:
        return self._family_combo.value()

    @checked
    def getSize(self : Self) -> FontSize | NoChange:
        return self._size_combo.value()

    @checked
    def getBold(self : Self) -> FontBool | NoChange:
        return self._bold_combo.value()

    @checked
    def getItalic(self : Self) -> FontBool | NoChange:
        return self._italic_combo.value()

    @checked
    def getUnderline(self : Self) -> FontBool | NoChange:
        return self._underline_combo.value()


class TextAppearancePreviewLayout(TextAppearanceLayout):
    _preview : QLabel

    @checked
    def __init__(
        self              : Self,
        initial_color     : Color      | NoChange,
        initial_family    : FontFamily | NoChange,
        initial_size      : FontSize   | NoChange,
        initial_bold      : FontBool   | NoChange,
        initial_italic    : FontBool   | NoChange,
        initial_underline : FontBool   | NoChange,
        default_color     : QColor,
        default_family    : str,
        default_size      : float,
        default_bold      : bool,
        default_italic    : bool,
        default_underline : bool,
        parent            : QWidget | None = None
    ) -> None:
        super().__init__(
            initial_color,
            initial_family,
            initial_size,
            initial_bold,
            initial_italic,
            initial_underline,
            default_color,
            default_family,
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
        self._family_combo.activated.connect(self._updatePreview)
        self._bold_combo.activated.connect(self._updatePreview)
        self._italic_combo.activated.connect(self._updatePreview)
        self._underline_combo.activated.connect(self._updatePreview)

    def _updatePreview(self : Self) -> None:
        family    = self._family_combo.value()
        family    = self._default_family if family == DEFAULT   else \
                    self._initial_family if family is NO_CHANGE else family
        bold      = self._bold_combo.value()
        bold      = self._default_bold if bold == DEFAULT   else \
                    self._initial_bold if bold is NO_CHANGE else bold
        italic    = self._italic_combo.value()
        italic    = self._default_italic if italic == DEFAULT   else \
                    self._initial_italic if italic is NO_CHANGE else italic
        underline = self._underline_combo.value()
        underline = self._default_underline if underline == DEFAULT   else \
                    self._initial_underline if underline is NO_CHANGE else underline
        if any(x in (DEFAULT, NO_CHANGE) for x in (family, bold, italic, underline)):
            self._preview.setText("") # options are ambiguous
            return
        font = QFont()
        font.setFamily(family)
        font.setPointSizeF(24.0) # TODO scale with dialog, or use settings?
        font.setBold(bold)
        font.setItalic(italic)
        font.setUnderline(underline)
        self._preview.setFont(font)
        self._preview.setText("Sample Text")
