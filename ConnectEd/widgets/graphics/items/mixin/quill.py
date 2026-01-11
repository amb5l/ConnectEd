from typing import Self, Protocol

from collections.abc import Callable

from PyQt6.QtGui  import QFont, QBrush, QColor

from .....app import logger, settings

from ...property import PropertySpec

from .. import Default, DEFAULT

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...scenes.drawing import DrawingScene


class ItemProtocol(Protocol):
    def settingsName(self) -> str: ...
    def addSelectionHandler(self, handler: Callable[[bool], None]) -> None: ...
    def color(self) -> QColor: ...
    def setColor(self, color: QColor) -> None: ...
    def font(self) -> QFont: ...
    def setFont(self, font: QFont) -> None: ...
    def scene(self) -> "DrawingScene": ...


class ItemQuillMixin:
    """Mixin for items that render text."""

    _PROPERTY_SPECS_QUILL = {
        "Text Color" : PropertySpec(
            kind    = "QColor",
            valid   = lambda self: self.quillColor() is not DEFAULT,
            getter  = lambda self: self.quillColor(),
            setter  = lambda self, value: self.setQuillColor(value),
            default = lambda self: self.defaultQuillColor()
        ),
        "Text Font" : PropertySpec(
            kind    = "FontFamily",  # a "subtype" of str - see str2val
            valid   = lambda self: self.quillFamily() is not DEFAULT,
            getter  = lambda self: self.quillFamily(),
            setter  = lambda self, value: self.setQuillFamily(value),
            default = lambda self: self.defaultQuillFamily()
        ),
        "Text Size" : PropertySpec(
            kind    = "FontSize",  # a "subtype" of float - see str2val
            valid   = lambda self: self.quillSize() is not DEFAULT,
            getter  = lambda self: self.quillSize(),
            setter  = lambda self, value: self.setQuillSize(value),
            default = lambda self: self.defaultQuillSize()
        ),
        "Text Bold" : PropertySpec(
            kind    = "bool",
            valid   = lambda self: self.quillBold() is not DEFAULT,
            getter  = lambda self: self.quillBold(),
            setter  = lambda self, value: self.setQuillBold(value),
            default = lambda self: self.defaultQuillBold()
        ),
        "Text Italic" : PropertySpec(
            kind    = "bool",
            valid   = lambda self: self.quillItalic() is not DEFAULT,
            getter  = lambda self: self.quillItalic(),
            setter  = lambda self, value: self.setQuillItalic(value),
            default = lambda self: self.defaultQuillItalic()
        ),
        "Text Underline" : PropertySpec(
            kind    = "bool",
            valid   = lambda self: self.quillUnderline() is not DEFAULT,
            getter  = lambda self: self.quillUnderline(),
            setter  = lambda self, value: self.setQuillUnderline(value),
            default = lambda self: self.defaultQuillUnderline()
        )
    }

    # instance attributes
    _quill_color     : QColor | Default
    _quill_family    : str    | Default
    _quill_size      : float  | Default
    _quill_bold      : bool   | Default
    _quill_italic    : bool   | Default
    _quill_underline : bool   | Default

    def initQuill(self : Self | ItemProtocol) -> None:
        if not hasattr(self, "setFont"):
            logger().error("This item does not support the setFont method")
        self._quill_color     = DEFAULT
        self._quill_family    = DEFAULT
        self._quill_size      = DEFAULT
        self._quill_bold      = DEFAULT
        self._quill_italic    = DEFAULT
        self._quill_underline = DEFAULT
        self.quillSettingsChange()
        settings().changed.connect(self.quillSettingsChange)
        self.addSelectionHandler(self.quillSelectionChange)

    def quillSettingsChange(self : Self | ItemProtocol) -> None:
        """Refresh following possible changes to default pen settings."""
        self.setQuillColor(self.quillColor())
        self.setQuillFamily(self.quillFamily())
        self.setQuillSize(self.quillSize())
        self.setQuillBold(self.quillBold())
        self.setQuillItalic(self.quillItalic())
        self.setQuillUnderline(self.quillUnderline())

    def quillSelectionChange(self : Self | ItemProtocol, selected : bool) -> None:
        scene : "DrawingScene" = self.scene()
        self.setQuillColor(scene.selectedQuillColor() if selected else self.quillColor())

    def defaultQuillColor(self : Self | ItemProtocol) -> QColor | Default:
        return settings().get(f"theme/items/{self.settingsName()}/text/color")

    def quillColor(self : Self | ItemProtocol) -> QColor | Default:
        return self._quill_color

    def setQuillColor(
        self  : Self | ItemProtocol,
        color : QColor | Default
    ) -> None:
        if color is DEFAULT: color = self.defaultQuillColor()
        self.setColor(color)

    def defaultQuillFamily(self : Self | ItemProtocol) -> str | Default:
        return settings().get(f"theme/items/{self.settingsName()}/text/font")

    def quillFamily(self : Self | ItemProtocol) -> str | Default:
        return self._quill_family

    def setQuillFamily(
        self   : Self | ItemProtocol,
        family : str | Default
    ) -> None:
        if family is DEFAULT: family = self.defaultQuillFamily()
        font = self.font()
        font.setFamily(family)
        self.setFont(font)

    def defaultQuillSize(self : Self | ItemProtocol) -> float | Default:
        return settings().get(f"theme/items/{self.settingsName()}/text/size")

    def quillSize(self : Self | ItemProtocol) -> float | Default:
        return self._quill_size

    def setQuillSize(
        self : Self | ItemProtocol,
        size : float | Default
    ) -> None:
        if size is DEFAULT: size = self.defaultQuillSize()
        font = self.font()
        font.setPointSizeF(size)
        self.setFont(font)

    def defaultQuillBold(self : Self | ItemProtocol) -> bool | Default:
        return settings().get(f"theme/items/{self.settingsName()}/text/bold")

    def quillBold(self : Self | ItemProtocol) -> bool | Default:
        return self._quill_bold

    def setQuillBold(
        self : Self | ItemProtocol,
        bold : bool | Default
    ) -> None:
        if bold is DEFAULT: bold = self.defaultQuillBold()
        font = self.font()
        font.setBold(bold)
        self.setFont(font)

    def defaultQuillItalic(self : Self | ItemProtocol) -> bool | Default:
        return settings().get(f"theme/items/{self.settingsName()}/text/italic")

    def quillItalic(self : Self | ItemProtocol) -> bool | Default:
        return self._quill_italic

    def setQuillItalic(
        self   : Self | ItemProtocol,
        italic : bool | Default
    ) -> None:
        if italic is DEFAULT: italic = self.defaultQuillItalic()
        font = self.font()
        font.setItalic(italic)
        self.setFont(font)

    def defaultQuillUnderline(self : Self | ItemProtocol) -> bool | Default:
        return settings().get(f"theme/items/{self.settingsName()}/text/underline")

    def quillUnderline(self : Self | ItemProtocol) -> bool | Default:
        return self._quill_underline

    def setQuillUnderline(
        self      : Self | ItemProtocol,
        underline : bool | Default
    ) -> None:
        if underline is DEFAULT: underline = self.defaultQuillUnderline()
        font = self.font()
        font.setUnderline(underline)
        self.setFont(font)
