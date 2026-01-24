from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel
from PyQt6.QtGui     import QFont, QColor

from ....graphics.items import Default, DEFAULT, NoChange, NO_CHANGE

from ..combo.color       import ColorComboBox
from ..combo.font_family import FontFamilyComboBox
from ..combo.font_size   import FontSizeComboBox
from ..combo.on_off      import OnOffComboBox


class TextAppearanceLayout(QVBoxLayout):
    _initial_color     : QColor | Default | NoChange
    _initial_family    : str    | Default | NoChange
    _initial_size      : float  | Default | NoChange
    _initial_bold      : bool   | Default | NoChange
    _initial_italic    : bool   | Default | NoChange
    _initial_underline : bool   | Default | NoChange
    _default_color     : QColor | Default
    _default_family    : str    | Default
    _default_size      : float  | Default
    _default_bold      : bool   | Default
    _default_italic    : bool   | Default
    _default_underline : bool   | Default
    _options_layout     : QGridLayout
    _color_label        : QLabel
    _color_combo        : ColorComboBox
    _family_label       : QLabel
    _family_combo       : FontFamilyComboBox
    _size_label         : QLabel
    _size_combo         : FontSizeComboBox
    _bold_label         : QLabel
    _bold_combo         : OnOffComboBox
    _italic_label       : QLabel
    _italic_combo       : OnOffComboBox
    _underline_label    : QLabel
    _underline_combo    : OnOffComboBox

    def __init__(
        self              : Self,
        initial_color     : QColor | Default | NoChange,
        initial_family    : str    | Default | NoChange,
        initial_size      : float  | Default | NoChange,
        initial_bold      : bool   | Default | NoChange,
        initial_italic    : bool   | Default | NoChange,
        initial_underline : bool   | Default | NoChange,
        default_color     : QColor | Default,
        default_family    : str    | Default,
        default_size      : float  | Default,
        default_bold      : bool   | Default,
        default_italic    : bool   | Default,
        default_underline : bool   | Default,
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
        self._family_label = QLabel("Family:")
        self._options_layout.addWidget(self._family_label, 1, 0)
        self._family_combo = FontFamilyComboBox(initial_family, default_family)
        self._options_layout.addWidget(self._family_combo, 1, 1)
        self._size_label = QLabel("Size:")
        self._options_layout.addWidget(self._size_label, 2, 0)
        self._size_combo = FontSizeComboBox(initial_size, default_size)
        self._options_layout.addWidget(self._size_combo, 2, 1)
        self._bold_label = QLabel("Bold:")
        self._options_layout.addWidget(self._bold_label, 3, 0)
        self._bold_combo = OnOffComboBox(initial_bold, default_bold)
        self._options_layout.addWidget(self._bold_combo, 3, 1)
        self._italic_label = QLabel("Italic:")
        self._options_layout.addWidget(self._italic_label, 4, 0)
        self._italic_combo = OnOffComboBox(initial_italic, default_italic)
        self._options_layout.addWidget(self._italic_combo, 4, 1)
        self._underline_label = QLabel("Underline:")
        self._options_layout.addWidget(self._underline_label, 5, 0)
        self._underline_combo = OnOffComboBox(initial_underline, default_underline)
        self._options_layout.addWidget(self._underline_combo, 5, 1)
        self.addLayout(self._options_layout)

    def getColor(self : Self) -> QColor | Default | NoChange:
        return self._color_combo.getChoice()

    def getFamily(self : Self) -> str | Default | NoChange:
        return self._family_combo.getChoice()

    def getSize(self : Self) -> float | NoChange | Default:
        return self._size_combo.getChoice()

    def getBold(self : Self) -> bool | Default | NoChange:
        return self._bold_combo.getChoice()

    def getItalic(self : Self) -> bool | Default | NoChange:
        return self._italic_combo.getChoice()

    def getUnderline(self : Self) -> bool | Default | NoChange:
        return self._underline_combo.getChoice()


class TextAppearancePreviewLayout(TextAppearanceLayout):
    _preview : QLabel

    def __init__(
        self              : Self,
        initial_color     : QColor | Default | NoChange,
        initial_family    : str    | Default | NoChange,
        initial_size      : float  | Default | NoChange,
        initial_bold      : bool   | Default | NoChange,
        initial_italic    : bool   | Default | NoChange,
        initial_underline : bool   | Default | NoChange,
        default_color     : QColor | Default,
        default_family    : str    | Default,
        default_size      : float  | Default,
        default_bold      : bool   | Default,
        default_italic    : bool   | Default,
        default_underline : bool   | Default,
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

    def _updatePreview(self : Self):
        family    = self._family_combo.getChoice()
        family    = self._default_family if family is DEFAULT   else \
                    self._initial_family if family is NO_CHANGE else family
        bold      = self._bold_combo.getChoice()
        bold      = self._default_bold if bold is DEFAULT   else \
                    self._initial_bold if bold is NO_CHANGE else bold
        italic    = self._italic_combo.getChoice()
        italic    = self._default_italic if italic is DEFAULT   else \
                    self._initial_italic if italic is NO_CHANGE else italic
        underline = self._underline_combo.getChoice()
        underline = self._default_underline if underline is DEFAULT   else \
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
