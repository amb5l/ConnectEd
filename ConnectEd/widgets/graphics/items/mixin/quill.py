from typing import Self

from ...properties import PropertySpec

from .. import Quill


class ElementQuillMixin:
    _PROPERTY_SPECS_QUILL = {
        "Text Color" : PropertySpec(
            type_name = "QColor",
            exists    = lambda self: self.quill is not None,
            getter    = lambda self: self.quill.getColor(),
            setter    = lambda self, value: self.quill.setColor(value),
            default   = lambda self: self.quill.getDefaults().color
        ),
        "Text Font" : PropertySpec(
            type_name = "str",
            exists    = lambda self: self.quill is not None,
            getter    = lambda self: self.quill.getFamily(),
            setter    = lambda self, value: self.quill.setFamily(value),
            default   = lambda self: self.quill.getDefaults().family
        ),
        "Text Size" : PropertySpec(
            type_name = "float",
            exists    = lambda self: self.quill is not None,
            getter    = lambda self: self.quill.getSize(),
            setter    = lambda self, value: self.quill.setSize(value),
            default   = lambda self: self.quill.getDefaults().size
        ),
        "Text Bold" : PropertySpec(
            type_name = "bool",
            exists    = lambda self: self.quill is not None,
            getter    = lambda self: self.quill.getBold(),
            setter    = lambda self, value: self.quill.setBold(value),
            default   = lambda self: self.quill.getDefaults().bold
        ),
        "Text Italic" : PropertySpec(
            type_name = "bool",
            exists    = lambda self: self.quill is not None,
            getter    = lambda self: self.quill.getItalic(),
            setter    = lambda self, value: self.quill.setItalic(value),
            default   = lambda self: self.quill.getDefaults().italic
        ),
        "Text Underline" : PropertySpec(
            type_name = "bool",
            exists    = lambda self: self.quill is not None,
            getter    = lambda self: self.quill.getUnderline(),
            setter    = lambda self, value: self.quill.setUnderline(value),
            default   = lambda self: self.quill.getDefaults().underline
        )
    }

    quill : Quill

    def initQuill(self : Self):
        self.quill = Quill(self)
