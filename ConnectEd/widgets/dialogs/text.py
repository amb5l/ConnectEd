__all__ = ["TextFontDialog"]

from typing import Self, Optional

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QDialog, QWidget, \
                            QVBoxLayout, QHBoxLayout, \
                            QComboBox, QCheckBox, QDialogButtonBox, QLabel
from PyQt6.QtGui     import QFontDatabase, QFont


class TextFontDialog(QDialog):
    def __init__(
        self      : Self,
        family    : tuple[ Optional[str]   , str   ], # spec, default
        size      : tuple[ Optional[float] , float ], # spec, default
        bold      : tuple[ Optional[bool]  , bool  ], # spec, default
        italic    : tuple[ Optional[bool]  , bool  ], # spec, default
        underline : tuple[ Optional[bool]  , bool  ], # spec, default
        parent    : Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.setWindowTitle("Text Font")
        self.setModal(True)
        self.chosen_family    , self.default_family    = family
        self.chosen_size      , self.default_size      = size
        self.chosen_bold      , self.default_bold      = bold
        self.chosen_italic    , self.default_italic    = italic
        self.chosen_underline , self.default_underline = underline

        # Initialize UI
        self._layout()

        # initial states
        if self.chosen_family:
            index = self.family_combo.findText(self.chosen_family)
            if index >= 0:
                self.family_combo.setCurrentIndex(index)
            else:
                self.family_combo.setCurrentIndex(0)  # <default>
        else:
            self.family_combo.setCurrentIndex(0)  # <default>

        if self.chosen_size:
            index = self.size_combo.findText(str(self.chosen_size))
            if index >= 0:
                self.size_combo.setCurrentIndex(index)
            else:
                self.size_combo.setCurrentIndex(0)  # <default>
        else:
            self.size_combo.setCurrentIndex(0)  # <default>

        self.bold_check.setCheckState(
            Qt.CheckState.Checked   if self.chosen_bold is True else
            Qt.CheckState.Unchecked if self.chosen_bold is False else
            Qt.CheckState.PartiallyChecked
        )
        self.italic_check.setCheckState(
            Qt.CheckState.Checked   if self.chosen_italic is True else
            Qt.CheckState.Unchecked if self.chosen_italic is False else
            Qt.CheckState.PartiallyChecked
        )
        self.underline_check.setCheckState(
            Qt.CheckState.Checked   if self.chosen_underline is True else
            Qt.CheckState.Unchecked if self.chosen_underline is False else
            Qt.CheckState.PartiallyChecked
        )

    def _layout(self):
        self.dialog_layout = QVBoxLayout(self)
        self.family_size = QHBoxLayout()
        self.options = QHBoxLayout()

        self.family_combo = QComboBox()
        font_families = QFontDatabase.families()
        self.family_combo.addItem("<default>", None)
        for family in sorted(font_families):
            self.family_combo.addItem(family, family)
        self.family_combo.currentIndexChanged.connect(self._update_family)
        self.family_size.addWidget(self.family_combo)

        self.size_combo = QComboBox()
        self.size_combo.addItem("<default>", None)
        for size in [6, 7, 8, 9, 10, 12, 14, 16, 18, 24, 36, 48, 72]:
            self.size_combo.addItem(str(size), size)
        self.size_combo.currentIndexChanged.connect(self._update_size)
        self.family_size.addWidget(self.size_combo)

        self.bold_check = QCheckBox("Bold")
        self.bold_check.setTristate(True)
        self.bold_check.stateChanged.connect(self._update_bold)
        self.options.addWidget(self.bold_check)

        self.italic_check = QCheckBox("Italic")
        self.italic_check.setTristate(True)
        self.italic_check.stateChanged.connect(self._update_italic)
        self.options.addWidget(self.italic_check)

        self.underline_check = QCheckBox("Underline")
        self.underline_check.setTristate(True)
        self.underline_check.stateChanged.connect(self._update_underline)
        self.options.addWidget(self.underline_check)

        self.preview = QLabel("Sample Text")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumHeight(40)
        #self.preview.setStyleSheet("border: 1px solid #cccccc; background: white;")

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok    |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.dialog_layout.addLayout(self.family_size)
        self.dialog_layout.addLayout(self.options)
        self.dialog_layout.addWidget(self.preview)
        self.dialog_layout.addWidget(self.button_box)

    def _update_family(self):
        self.chosen_family = (
            None if self.family_combo.currentIndex() == 0 else
            self.family_combo.currentData()
        )
        self._update_preview()

    def _update_size(self):
        self.chosen_size = (
            None if self.size_combo.currentIndex() == 0 else
            float(self.size_combo.currentData())
        )
        self._update_preview()

    def _update_bold(self):
        self.chosen_bold = (
            True  if self.bold_check.checkState() == Qt.CheckState.Checked else
            False if self.bold_check.checkState() == Qt.CheckState.Unchecked else
            None
        )
        self._update_preview()

    def _update_italic(self):
        self.chosen_italic = (
            True  if self.italic_check.checkState() == Qt.CheckState.Checked else
            False if self.italic_check.checkState() == Qt.CheckState.Unchecked else
            None
        )
        self._update_preview()

    def _update_underline(self):
        self.chosen_underline = (
            True  if self.underline_check.checkState() == Qt.CheckState.Checked else
            False if self.underline_check.checkState() == Qt.CheckState.Unchecked else
            None
        )
        self._update_preview()

    def _update_preview(self):
        font = QFont()
        font.setFamily(
            self.default_family if self.chosen_family is None else
            self.chosen_family
        )
        font.setPointSizeF(24.0) # TODO scale with dialog, or use settings?
        font.setBold(
            self.default_bold if self.chosen_bold is None else
            self.chosen_bold
        )
        font.setItalic(
            self.default_italic if self.chosen_italic is None else
            self.chosen_italic
        )
        font.setUnderline(
            self.default_underline if self.chosen_underline is None else
            self.chosen_underline
        )
        self.preview.setFont(font)
