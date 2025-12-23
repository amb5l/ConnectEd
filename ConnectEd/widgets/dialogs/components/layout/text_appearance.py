from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
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
    options_layout     : QVBoxLayout
    color_layout       : QHBoxLayout
    color_label        : QLabel
    color_combo        : ColorComboBox
    family_layout      : QHBoxLayout
    family_label       : QLabel
    family_combo       : FontFamilyComboBox
    size_layout        : QHBoxLayout
    size_label         : QLabel
    size_combo         : FontSizeComboBox
    bold_layout        : QHBoxLayout
    bold_label         : QLabel
    bold_combo         : OnOffComboBox
    italic_layout      : QHBoxLayout
    italic_label       : QLabel
    italic_combo       : OnOffComboBox
    underline_layout   : QHBoxLayout
    underline_label    : QLabel
    underline_combo    : OnOffComboBox
    preview            : QLabel

    def __init__(self : Self,
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
        self.options_layout = QVBoxLayout()
        self.color_layout = QHBoxLayout()
        self.color_label = QLabel("Color:")
        self.color_layout.addWidget(self.color_label)
        self.color_combo = ColorComboBox(initial_color, default_color)
        self.color_layout.addWidget(self.color_combo)
        self.options_layout.addWidget(self.color_layout)
        self.family_layout = QHBoxLayout()
        self.family_label = QLabel("Family:")
        self.family_layout.addWidget(self.family_label)
        self.family_combo = FontFamilyComboBox(initial_family, default_family)
        self.family_layout.addWidget(self.family_combo)
        self.options_layout.addWidget(self.family_layout)
        self.size_layout = QHBoxLayout()
        self.size_label = QLabel("Size:")
        self.size_layout.addWidget(self.size_label)
        self.size_combo = FontSizeComboBox(initial_size, default_size)
        self.size_layout.addWidget(self.size_combo)
        self.options_layout.addWidget(self.size_layout)
        self.bold_layout = QHBoxLayout()
        self.bold_label = QLabel("Bold:")
        self.bold_layout.addWidget(self.bold_label)
        self.bold_combo = OnOffComboBox(initial_bold, default_bold)
        self.bold_layout.addWidget(self.bold_combo)
        self.options_layout.addWidget(self.bold_layout)
        self.italic_layout = QHBoxLayout()
        self.italic_label = QLabel("Italic:")
        self.italic_layout.addWidget(self.italic_label)
        self.italic_combo = OnOffComboBox(initial_italic, default_italic)
        self.italic_layout.addWidget(self.italic_combo)
        self.options_layout.addWidget(self.italic_layout)
        self.underline_layout = QHBoxLayout()
        self.underline_label = QLabel("Underline:")
        self.underline_layout.addWidget(self.underline_label)
        self.underline_combo = OnOffComboBox(initial_underline, default_underline)
        self.underline_layout.addWidget(self.underline_combo)
        self.options_layout.addWidget(self.underline_layout)
        self.addLayout(self.options_layout)
        self.preview = QLabel("Sample Text")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumHeight(40)
        self.updatePreview()
        self.addWidget(self.preview)
        self.family_combo.activated.connect(self.updatePreview)
        self.bold_combo.activated.connect(self.updatePreview)
        self.italic_combo.activated.connect(self.updatePreview)
        self.underline_combo.activated.connect(self.updatePreview)

    def updatePreview(self : Self):
        family    = self.family_combo.getChoice()
        family    = self._default_family if family is DEFAULT   else \
                    self._initial_family if family is NO_CHANGE else family
        bold      = self.bold_combo.getChoice()
        bold      = self._default_bold if bold is DEFAULT   else \
                    self._initial_bold if bold is NO_CHANGE else bold
        italic    = self.italic_combo.getChoice()
        italic    = self._default_italic if italic is DEFAULT   else \
                    self._initial_italic if italic is NO_CHANGE else italic
        underline = self.underline_combo.getChoice()
        underline = self._default_underline if underline is DEFAULT   else \
                    self._initial_underline if underline is NO_CHANGE else underline
        if any(x in (DEFAULT, NO_CHANGE) for x in (family, bold, italic, underline)):
            self.preview.setText("") # options are ambiguous
            return
        font = QFont()
        font.setFamily(family)
        font.setPointSizeF(24.0) # TODO scale with dialog, or use settings?
        font.setBold(bold)
        font.setItalic(italic)
        font.setUnderline(underline)
        self.preview.setFont(font)
        self.preview.setText("Sample Text")

    def getColor(self : Self) -> QColor | Default | NoChange:
        return self.color_combo.getChoice()

    def getFamily(self : Self) -> str | Default | NoChange:
        return self.family_combo.getChoice()

    def getSize(self : Self) -> float | NoChange | Default:
        return self.size_combo.getChoice()

    def getBold(self : Self) -> bool | Default | NoChange:
        return self.bold_combo.getChoice()

    def getItalic(self : Self) -> bool | Default | NoChange:
        return self.italic_combo.getChoice()

    def getUnderline(self : Self) -> bool | Default | NoChange:
        return self.underline_combo.getChoice()
