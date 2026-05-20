from typing import Self

from PyQt6.QtWidgets import QGraphicsView
from PyQt6.QtGui     import QColor

from ......app import logger

from ......core.types import NoChange, NO_CHANGE

from ....quill  import Quill

from ....scenes import withScene

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....scenes.drawing import DrawingScene
    from . import MixinType as ItemType


class ItemPresentationTextMixin:

    # API

    def hasText(self : "Self | ItemType") -> bool:
        return (
               self.hasTextColor()
            or self.hasTextFont()
            or self.hasTextSize()
            or self.hasTextBold()
            or self.hasTextItalic()
            or self.hasTextUnderline()
        )

    def hasTextColor(self : "Self | ItemType") -> bool:
        return hasattr(self, "_text_color")

    def textColor(self : "Self | ItemType") -> QColor | None:
        return self._text_color if hasattr(self, "_text_color") else None

    def defaultTextColor(
        self   : "Self | ItemType",
        widget : "QGraphicsView | None" = None
    ) -> QColor | None:
        scene = self._defaultScene(widget)
        key = self._quillKeyDefault()
        quill = scene.resources.quill(self.resourcesName(), key)
        return quill.color()

    def setTextColor(self : "Self | ItemType", color: QColor | None | NoChange) -> None:
        if color is NO_CHANGE:
            return
        if not hasattr(self, "_text_color"):
            logger().error("This item does not support text color overrides.")
            return
        self._text_color = color
        self._updateQuill()

    def hasTextFont(self : "Self | ItemType") -> bool:
        return hasattr(self, "_text_font")

    def textFont(self : "Self | ItemType") -> str | None:
        return self._text_font if hasattr(self, "_text_font") else None

    def defaultTextFont(
        self   : "Self | ItemType",
        widget : "QGraphicsView | None" = None
    ) -> str | None:
        scene = self._defaultScene(widget)
        key = self._quillKeyDefault()
        quill = scene.resources.quill(self.resourcesName(), key)
        return quill.font()

    def setTextFont(self : "Self | ItemType", font: str | None | NoChange) -> None:
        if font is NO_CHANGE:
            return
        if not hasattr(self, "_text_font"):
            logger().error("This item does not support text font overrides.")
            return
        self._text_font = font
        self._updateQuill()

    def hasTextSize(self : "Self | ItemType") -> bool:
        return hasattr(self, "_text_size")

    def textSize(self : "Self | ItemType") -> float | None:
        return self._text_size if hasattr(self, "_text_size") else None

    def defaultTextSize(
        self   : "Self | ItemType",
        widget : "QGraphicsView | None" = None
    ) -> float | None:
        scene = self._defaultScene(widget)
        key = self._quillKeyDefault()
        quill = scene.resources.quill(self.resourcesName(), key)
        return quill.size()

    def setTextSize(self : "Self | ItemType", size: float | None | NoChange) -> None:
        if size is NO_CHANGE:
            return
        if not hasattr(self, "_text_size"):
            logger().error("This item does not support text size overrides.")
            return
        self._text_size = size
        self._updateQuill()

    def hasTextBold(self : "Self | ItemType") -> bool:
        return hasattr(self, "_text_bold")

    def textBold(self : "Self | ItemType") -> bool | None:
        return self._text_bold if hasattr(self, "_text_bold") else None

    def defaultTextBold(
        self   : "Self | ItemType",
        widget : "QGraphicsView | None" = None
    ) -> bool | None:
        scene = self._defaultScene(widget)
        key = self._quillKeyDefault()
        quill = scene.resources.quill(self.resourcesName(), key)
        return quill.bold()

    def setTextBold(self : "Self | ItemType", bold: bool | None | NoChange) -> None:
        if bold is NO_CHANGE:
            return
        if not hasattr(self, "_text_bold"):
            logger().error("This item does not support text bold overrides.")
            return
        self._text_bold = bold
        self._updateQuill()

    def hasTextItalic(self : "Self | ItemType") -> bool:
        return hasattr(self, "_text_italic")

    def textItalic(self : "Self | ItemType") -> bool | None:
        return self._text_italic if hasattr(self, "_text_italic") else None

    def defaultTextItalic(
        self   : "Self | ItemType",
        widget : "QGraphicsView | None" = None
    ) -> bool | None:
        scene = self._defaultScene(widget)
        key = self._quillKeyDefault()
        quill = scene.resources.quill(self.resourcesName(), key)
        return quill.italic()

    def setTextItalic(self : "Self | ItemType", italic: bool | None | NoChange) -> None:
        if italic is NO_CHANGE:
            return
        if not hasattr(self, "_text_italic"):
            logger().error("This item does not support text italic overrides.")
            return
        self._text_italic = italic
        self._updateQuill()

    def hasTextUnderline(self : "Self | ItemType") -> bool:
        return hasattr(self, "_text_underline")

    def textUnderline(self : "Self | ItemType") -> bool | None:
        return self._text_underline if hasattr(self, "_text_underline") else None

    def defaultTextUnderline(
        self   : "Self | ItemType",
        widget : "QGraphicsView | None" = None
    ) -> bool | None:
        scene = self._defaultScene(widget)
        key = self._quillKeyDefault()
        quill = scene.resources.quill(self.resourcesName(), key)
        return quill.underline()

    def setTextUnderline(self : "Self | ItemType", underline: bool | None | NoChange) -> None:
        if underline is NO_CHANGE:
            return
        if not hasattr(self, "_text_underline"):
            logger().error("This item does not support text underline overrides.")
            return
        self._text_underline = underline
        self._updateQuill()

    # helpers

    def _quillKey(self : "Self | ItemType") -> bool:
        return self.isSelected()

    def _quillKeyDefault(self : "Self | ItemType") -> bool:
        return False

    @withScene
    def _updateQuill(self : "Self | ItemType") -> None:
        raise NotImplementedError("Not wired!")

    @withScene
    def _updateQuillFast(self : "Self | ItemType", scene : "DrawingScene") -> None:
        quill = scene.resources.quill(self.resourcesName(), self._quillKey())
        self.setQuill(quill)

    @withScene
    def _updateQuillSlow(self : "Self | ItemType", scene : "DrawingScene") -> None:
        quill = scene.resources.quill(self.resourcesName(), self._quillKey())
        override_color = \
            hasattr(self, "_text_color") and not self.isSelected() \
                and self._text_color is not None
        override_font = \
            hasattr(self, "_text_font") and self._text_font is not None
        override_size = \
            hasattr(self, "_text_size") and self._text_size is not None
        override_bold = \
            hasattr(self, "_text_bold") and self._text_bold is not None
        override_italic = \
            hasattr(self, "_text_italic") and self._text_italic is not None
        override_underline = \
            hasattr(self, "_text_underline") and self._text_underline is not None
        if override_color \
        or override_font \
        or override_size \
        or override_bold \
        or override_italic \
        or override_underline:
            quill = Quill(quill)
            if override_color: quill.setColor(self._text_color)
            if override_font: quill.setFont(self._text_font)
            if override_size: quill.setSize(self._text_size)
            if override_bold: quill.setBold(self._text_bold)
            if override_italic: quill.setItalic(self._text_italic)
            if override_underline: quill.setUnderline(self._text_underline)
        self.setQuill(quill)
