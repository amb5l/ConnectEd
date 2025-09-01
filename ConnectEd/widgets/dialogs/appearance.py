from typing import Self, Optional
from dataclasses import dataclass

from PyQt6.QtWidgets import QWidget, QDialog, QPushButton, QGroupBox, \
                            QVBoxLayout, QHBoxLayout

from ...core.log import logger

from ..graphics.items import \
    DEFAULT, NO_CHANGE, \
    LineSpec,LinePref, LinePrefDefault, LinePrefChange, \
    FillSpec, FillPref, FillPrefDefault, FillPrefChange, \
    QuillSpec, QuillPref, QuillPrefDefault, QuillPrefChange

from ..graphics.items.mixin.line  import ElementLineMixin
from ..graphics.items.mixin.fill  import ElementFillMixin
from ..graphics.items.mixin.quill import ElementQuillMixin

from . import okCancelLayout

from .components import LineAppearanceLayout, \
                        FillAppearanceLayout, \
                        TextAppearanceLayout

@dataclass
class AppearanceSpec:
    line  : Optional[LineSpec]  = None
    fill  : Optional[FillSpec]  = None
    quill : Optional[QuillSpec] = None

@dataclass
class AppearancePref:
    line  : Optional[LinePref]  = None
    fill  : Optional[FillPref]  = None
    quill : Optional[QuillPref] = None

@dataclass
class AppearancePrefChange:
    line  : Optional[LinePrefChange]  = None
    fill  : Optional[FillPrefChange]  = None
    quill : Optional[QuillPrefChange] = None


class AppearanceDialog(QDialog):
    _dialog_layout    : QVBoxLayout
    _line_group_box   : Optional[QGroupBox]
    _line_layout      : Optional[LineAppearanceLayout]
    _fill_group_box   : Optional[QGroupBox]
    _fill_layout      : Optional[FillAppearanceLayout]
    _text_group_box   : Optional[QGroupBox]
    _text_layout      : Optional[TextAppearanceLayout]
    _ok_cancel_layout : QHBoxLayout
    _ok_button        : QPushButton
    _cancel_button    : QPushButton

    def __init__(
        self     : Self,
        elements : list[ElementLineMixin | ElementFillMixin |ElementQuillMixin],
        parent   : Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        initial   = AppearancePrefChange()
        no_change = AppearancePrefChange()
        default   = AppearanceSpec()
        for element in elements:
            for cat_name in ["line", "fill", "quill"]:
                if not hasattr(element, cat_name):
                    continue
                cat = getattr(element, cat_name)
                if cat is None:
                    continue
                pref = cat.getPref()
                for subcat_name in \
                 ["color", "width", "style"] if cat_name == "line" else \
                 ["color", "style"] if cat_name == "fill" else \
                 ["color", "family", "size", "bold", "italic", "underline"]:
                    subcat = getattr(pref, subcat_name)
                    if subcat is None:
                        logger.error(f"{cat_name}/{subcat_name} is None for element {element}")
                        continue
                    # populate no_change values
                    n_cat = getattr(no_change, cat_name)
                    if n_cat is None:
                        n_cat = LinePrefChange() if cat_name == "line" else \
                                FillPrefChange() if cat_name == "fill" else \
                                QuillPrefChange() if cat_name == "quill" else \
                                None
                        setattr(no_change, cat_name, n_cat)
                    n_subcat = getattr(n_cat, subcat_name)
                    if n_subcat is None:
                        n_subcat = subcat
                    elif n_subcat != subcat:
                        n_subcat = NO_CHANGE
                    setattr(n_cat, subcat_name, n_subcat)
                    # populate initial values
                    i_cat = getattr(initial, cat_name)
                    if i_cat is None:
                        i_cat = LinePrefChange() if cat_name == "line" else \
                                FillPrefChange() if cat_name == "fill" else \
                                QuillPrefChange() if cat_name == "quill" else \
                                None
                        setattr(initial, cat_name, i_cat)
                    i_subcat = getattr(i_cat, subcat_name)
                    if i_subcat is None:
                        i_subcat = subcat
                    elif i_subcat != subcat:
                        i_subcat = NO_CHANGE
                    setattr(i_cat, subcat_name, i_subcat)
                    # populate default values
                    d_cat = getattr(element, cat_name).getDefaults()
                    if d_cat is None:
                        logger.error(f"{cat_name} is None in defaults for element {element}")
                        continue
                    if not hasattr(d_cat, subcat_name):
                        logger.error(f"No {cat_name}/{subcat_name} attribute in defaults for element {element}")
                        continue
                    d_subcat = getattr(d_cat, subcat_name)
                    if d_subcat is None:
                        logger.error(f"{cat_name}/{subcat_name} is None in defaults for element {element}")
                        continue
                    v_cat = getattr(default, cat_name)
                    if v_cat is None:
                        v_cat = LinePrefDefault() if cat_name == "line" else \
                                FillPrefDefault() if cat_name == "fill" else \
                                QuillPrefDefault() if cat_name == "quill" else \
                                None
                        setattr(default, cat_name, v_cat)
                    v_subcat = getattr(v_cat, subcat_name)
                    if v_subcat is None:
                        v_subcat = d_subcat
                    elif d_subcat != v_subcat:
                        v_subcat = DEFAULT
                    setattr(v_cat, subcat_name, v_subcat)
        categories = \
            (0 if initial.line  is None else 1) + \
            (0 if initial.fill  is None else 1) + \
            (0 if initial.quill is None else 1)
        if categories == 0:
            logger.warning("No appearance data found in element(s)")
            return
        if categories > 1:
            title = "Appearance"
        else:
            title = (
                "Line Appearance" if initial.line is not None else
                "Fill Appearance" if initial.fill is not None else
                "Text Appearance"
            )
        if len(elements) > 1:
            title += f" ({len(elements)} elements)"
        self.setWindowTitle(title)
        self._dialog_layout = QVBoxLayout()
        if initial.line is not None:
            self.line_group_box = QGroupBox("Line") if categories > 1 else None
            self._line_layout = LineAppearanceLayout(
                initial.line,
                default.line,
                no_change.line
            )
            if categories > 1:
                self.line_group_box.setLayout(self._line_layout)
                self._dialog_layout.addWidget(self.line_group_box)
            else:
                self._dialog_layout.addLayout(self._line_layout)
        else:
            self.line_group_box = None
            self._line_layout    = None
        if initial.fill is not None:
            self._fill_group_box = QGroupBox("Fill") if categories > 1 else None
            self._fill_layout = FillAppearanceLayout(
                initial.fill,
                default.fill,
                no_change.fill
            )
            if categories > 1:
                self._fill_group_box.setLayout(self._fill_layout)
                self._dialog_layout.addWidget(self._fill_group_box)
            else:
                self._dialog_layout.addLayout(self._fill_layout)
        else:
            self._fill_group_box = None
            self._fill_layout    = None
        if initial.quill is not None:
            self._text_group_box = QGroupBox("Text") if categories > 1 else None
            self._text_layout = TextAppearanceLayout(
                initial.quill,
                default.quill,
                no_change.quill
            )
            if categories > 1:
                self._text_group_box.setLayout(self._text_layout)
                self._dialog_layout.addWidget(self._text_group_box)
            else:
                self._dialog_layout.addLayout(self._text_layout)
        else:
            self._text_group_box = None
            self._text_layout    = None
        okCancelLayout(self)
        self.setLayout(self._dialog_layout)

    def _adjustComboBoxWidths(self : Self) -> None:
        """Find all combo boxes in the dialog and set them to the width of the widest one."""
        combo_boxes = []

        # Collect all combo boxes from all layouts
        if self._line_layout is not None:
            for attr_name in ['color_combo', 'width_combo', 'style_combo']:
                if hasattr(self._line_layout, attr_name):
                    combo_boxes.append(getattr(self._line_layout, attr_name))

        if self._fill_layout is not None:
            for attr_name in ['color_combo', 'style_combo']:
                if hasattr(self._fill_layout, attr_name):
                    combo_boxes.append(getattr(self._fill_layout, attr_name))

        if self._text_layout is not None:
            for attr_name in ['color_combo', 'family_combo', 'size_combo',
                            'bold_combo', 'italic_combo', 'underline_combo']:
                if hasattr(self._text_layout, attr_name):
                    combo_boxes.append(getattr(self._text_layout, attr_name))

        if not combo_boxes:
            return

        # Find the maximum width
        max_width = 0
        for combo in combo_boxes:
            # Get the minimum size hint and actual size
            size_hint = combo.sizeHint()
            current_width = max(size_hint.width(), combo.width())
            max_width = max(max_width, current_width)

        # Set all combo boxes to the maximum width
        for combo in combo_boxes:
            combo.setMinimumWidth(max_width)

    def showEvent(self, event):
        """Override showEvent to adjust combo box widths after layout is complete."""
        super().showEvent(event)
        # Use QTimer.singleShot to defer the width adjustment until after the event loop
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, self._adjustComboBoxWidths)

    def getChoice(self : Self) -> AppearancePrefChange:
        r = AppearancePrefChange()
        if self._line_layout is not None:
            r.line = self._line_layout.getChoice()
        if self._fill_layout is not None:
            r.fill = self._fill_layout.getChoice()
        if self._text_layout is not None:
            r.quill = self._text_layout.getChoice()
        return r
