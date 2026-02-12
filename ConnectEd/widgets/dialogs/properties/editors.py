from typing import Self

from PyQt6.QtWidgets import QWidget

from ...graphics.properties import PropertyDisplay

from ...graphics.items import AlignH, AlignV

from ..components.edit  import (
    TextLineEditor,
    FloatEditor
)
from ..components.combo.enum import EnumComboBox
    StaticComboBox,
    DynamicComboBox,
    ColorComboBox,
    FontFamilyComboBox,
    FontSizeComboBox,
    FontBoolComboBox
)


class NameEditor(TextLineEditor):
    pass


class DisplayEditor(EnumComboBox[PropertyDisplay]):
    pass


class CleatEditor(DynamicComboBox[str]):
    def __init__(
        self    : Self,
        value   : str,
        choices : list[str],
        parent  : QWidget | None = None
    ) -> None:
        super().__init__(value, choices, parent)


class XEditor(FloatEditor):
    pass


class YEditor(FloatEditor):
    pass


class OriginEditor(StaticComboBox[str]):
    _CHOICES = [
        f"{v} {h}" \
            for v in ["Top", "Middle", "Bottom"] \
                for h in ["Left", "Center", "Right"]
    ]


class AlignHEditor(EnumComboBox[AlignH]):
    pass


class AlignVEditor(EnumComboBox[AlignV]):
    pass


class WidthEditor(FloatEditor):
    pass


class HeightEditor(FloatEditor):
    pass


class ColorEditor(ColorComboBox):
    pass


class FontFamilyEditor(FontFamilyComboBox):
    pass


class FontSizeEditor(FontSizeComboBox):
    pass


class BoldEditor(FontBoolComboBox):
    pass


class ItalicEditor(FontBoolComboBox):
    pass


class UnderlineEditor(FontBoolComboBox):
    pass
