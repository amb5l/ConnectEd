from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel
from PyQt6.QtGui     import QFont

from ....graphics.items import QuillPrefChange, QuillPref, DEFAULT, NO_CHANGE, QuillSpec

from ..combo.color       import ColorComboBox
from ..combo.font_family import FontFamilyComboBox
from ..combo.font_size   import FontSizeComboBox
from ..combo.on_off      import OnOffComboBox


class TextAppearanceLayout(QVBoxLayout):
    no_change       : QuillPrefChange
    default         : QuillPref
    options_layout  : QGridLayout
    color_label     : QLabel
    color_combo     : ColorComboBox
    family_label    : QLabel
    family_combo    : FontFamilyComboBox
    size_label      : QLabel
    size_combo      : FontSizeComboBox
    bold_label      : QLabel
    bold_combo      : OnOffComboBox
    italic_label    : QLabel
    italic_combo    : OnOffComboBox
    underline_label : QLabel
    underline_combo : OnOffComboBox
    preview         : QLabel

    def __init__(self : Self,
        initial   : QuillPrefChange | QuillPref,
        default   : QuillPref | QuillSpec,
        no_change : QuillPrefChange | None = None,
        parent    : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.no_change = no_change
        self.default   = default
        self.options_layout = QGridLayout()
        row = 0
        if initial.color is not None:
            self.color_label = QLabel("Color:")
            self.options_layout.addWidget(self.color_label, row, 0)
            self.color_combo = ColorComboBox(
                initial.color,
                default.color,
                None if no_change is None else no_change.color,
            )
            self.options_layout.addWidget(self.color_combo, row, 1)
            row += 1
        if initial.family is not None:
            self.family_label = QLabel("Family:")
            self.options_layout.addWidget(self.family_label, row, 0)
            self.family_combo = FontFamilyComboBox(
                initial.family,
                default.family,
                None if no_change is None else no_change.family,
            )
            self.options_layout.addWidget(self.family_combo, row, 1)
            row += 1
        if initial.size is not None:
            self.size_label = QLabel("Size:")
            self.options_layout.addWidget(self.size_label, row, 0)
            self.size_combo = FontSizeComboBox(
                initial.size,
                default.size,
                None if no_change is None else no_change.size,
            )
            self.options_layout.addWidget(self.size_combo, row, 1)
            row += 1
        if initial.bold is not None:
            self.bold_label = QLabel("Bold:")
            self.options_layout.addWidget(self.bold_label, row, 0)
            self.bold_combo = OnOffComboBox(
                initial.bold,
                default.bold,
                None if no_change is None else no_change.bold,
            )
            self.options_layout.addWidget(self.bold_combo, row, 1)
            row += 1
        if initial.italic is not None:
            self.italic_label = QLabel("Italic:")
            self.options_layout.addWidget(self.italic_label, row, 0)
            self.italic_combo = OnOffComboBox(
                initial.italic,
                default.italic,
                None if no_change is None else no_change.italic,
            )
            self.options_layout.addWidget(self.italic_combo, row, 1)
            row += 1
        if initial.underline is not None:
            self.underline_label = QLabel("Underline:")
            self.options_layout.addWidget(self.underline_label, row, 0)
            self.underline_combo = OnOffComboBox(
                initial.underline,
                default.underline,
                None if no_change is None else no_change.underline,
            )
            self.options_layout.addWidget(self.underline_combo, row, 1)
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
        family    = self.default.family   if family is DEFAULT else \
                    self.no_change.family if family is NO_CHANGE else \
                    family
        bold      = self.bold_combo.getChoice()
        bold      = self.default.bold   if bold is DEFAULT else \
                    self.no_change.bold if bold is NO_CHANGE else \
                    bold
        italic    = self.italic_combo.getChoice()
        italic    = self.default.italic if italic is DEFAULT else \
                    self.no_change.italic if italic is NO_CHANGE else \
                    italic
        underline = self.underline_combo.getChoice()
        underline = self.default.underline if underline is DEFAULT else \
                    self.no_change.underline if underline is NO_CHANGE else \
                    underline
        if family    is DEFAULT or family    is NO_CHANGE \
        or bold      is DEFAULT or bold      is NO_CHANGE \
        or italic    is DEFAULT or italic    is NO_CHANGE \
        or underline is DEFAULT or underline is NO_CHANGE:
            self.preview.setText("") # options are ambiguous
        else:
            font = QFont()
            font.setFamily(family)
            font.setPointSizeF(24.0) # TODO scale with dialog, or use settings?
            font.setBold(bold)
            font.setItalic(italic)
            font.setUnderline(underline)
            self.preview.setFont(font)
            self.preview.setText("Sample Text")

    def getChoice(self : Self) -> QuillPrefChange:
        r = QuillPrefChange()
        if hasattr(self, "color_combo"):
            r.color = self.color_combo.getChoice()
        if hasattr(self, "family_combo"):
            r.family = self.family_combo.getChoice()
        if hasattr(self, "size_combo"):
            r.size = self.size_combo.getChoice()
        if hasattr(self, "bold_combo"):
            r.bold = self.bold_combo.getChoice()
        if hasattr(self, "italic_combo"):
            r.italic = self.italic_combo.getChoice()
        if hasattr(self, "underline_combo"):
            r.underline = self.underline_combo.getChoice()
        return r
