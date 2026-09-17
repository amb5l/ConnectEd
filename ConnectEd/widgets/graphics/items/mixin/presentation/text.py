from __future__ import annotations

from typing import Self

from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QColor

from ......app import logger

from ......core.check import checked
from ......core.types import NoChange

from ....quill  import Quill

from ....properties import PropertiesMixin

from ....scenes import withScene

from ...protocols import SetQuillProtocol

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....views.diagram  import DiagramView
    from ....scenes.diagram import DiagramScene


class ItemPresentationTextMixin:

    _text_color     : QColor | None
    _text_font      : str    | None
    _text_size      : float  | None
    _text_bold      : bool   | None
    _text_italic    : bool   | None
    _text_underline : bool   | None

    @classmethod
    def themeQuill(cls : type[Self], scene : DiagramScene) -> Quill:
        return scene.resources.quill(
            cls.resourcesName(),
            cls._resourceNormalKey(),
        )

    def hasText(self : Self) -> bool:
        return (
               self.hasTextColor()
            or self.hasTextFont()
            or self.hasTextSize()
            or self.hasTextBold()
            or self.hasTextItalic()
            or self.hasTextUnderline()
        )

    def hasTextColor(self : Self) -> bool:
        return hasattr(self, "_text_color")

    def textColor(self : Self) -> QColor | None:
        return self._text_color if hasattr(self, "_text_color") else None

    def themeTextColor(
        self : Self,
        view : DiagramView | None = None
    ) -> QColor | None:
        """
        Get default from scene resources.
        Get scene from view if item not in scene yet.
        """
        from .. import ItemNamesMixin
        from . import ItemPresentationMixin
        if not isinstance(self, ItemPresentationMixin) \
        or not isinstance(self, ItemNamesMixin):
            raise TypeError("Bad host")
        if (scene := self._defaultScene(view)) is None:
            return None
        key = self._resourceNormalKey()
        quill = scene.resources.quill(self.resourcesName(), key)
        return quill.color()

    @checked
    def setTextColor(self : Self, color: QColor | None | NoChange) -> None:
        if isinstance(color, NoChange):
            return
        if not hasattr(self, "_text_color"):
            logger().error("This item does not support text color overrides.")
            return
        self._text_color = color
        self._updateQuill()
        if isinstance(self, PropertiesMixin):
            self.properties["Text Color"].notify()

    def hasTextFont(self : Self) -> bool:
        return hasattr(self, "_text_font")

    def textFont(self : Self) -> str | None:
        return self._text_font if hasattr(self, "_text_font") else None

    def themeTextFont(
        self : Self,
        view : DiagramView | None = None
    ) -> str | None:
        from .. import ItemNamesMixin
        from . import ItemPresentationMixin
        if not isinstance(self, ItemPresentationMixin) \
        or not isinstance(self, ItemNamesMixin):
            raise TypeError("Bad host")
        if (scene := self._defaultScene(view)) is None:
            return None
        key = self._resourceNormalKey()
        quill = scene.resources.quill(self.resourcesName(), key)
        return quill.font()

    @checked
    def setTextFont(self : Self, font: str | None | NoChange) -> None:
        if isinstance(font, NoChange):
            return
        if not hasattr(self, "_text_font"):
            logger().error("This item does not support text font overrides.")
            return
        self._text_font = font
        self._updateQuill()
        if isinstance(self, PropertiesMixin):
            self.properties["Text Font"].notify()

    def hasTextSize(self : Self) -> bool:
        return hasattr(self, "_text_size")

    def textSize(self : Self) -> float | None:
        return self._text_size if hasattr(self, "_text_size") else None

    def themeTextSize(
        self : Self,
        view : DiagramView | None = None
    ) -> float | None:
        from .. import ItemNamesMixin
        from . import ItemPresentationMixin
        if not isinstance(self, ItemPresentationMixin) \
        or not isinstance(self, ItemNamesMixin):
            raise TypeError("Bad host")
        if (scene := self._defaultScene(view)) is None:
            return None
        key = self._resourceNormalKey()
        quill = scene.resources.quill(self.resourcesName(), key)
        return quill.size()

    @checked
    def setTextSize(self : Self, size: float | None | NoChange) -> None:
        if isinstance(size, NoChange):
            return
        if not hasattr(self, "_text_size"):
            logger().error("This item does not support text size overrides.")
            return
        self._text_size = size
        self._updateQuill()
        if isinstance(self, PropertiesMixin):
            self.properties["Text Size"].notify()

    def hasTextBold(self : Self) -> bool:
        return hasattr(self, "_text_bold")

    def textBold(self : Self) -> bool | None:
        return self._text_bold if hasattr(self, "_text_bold") else None

    def themeTextBold(
        self : Self,
        view : DiagramView | None = None
    ) -> bool | None:
        from .. import ItemNamesMixin
        from . import ItemPresentationMixin
        if not isinstance(self, ItemPresentationMixin) \
        or not isinstance(self, ItemNamesMixin):
            raise TypeError("Bad host")
        if (scene := self._defaultScene(view)) is None:
            return None
        key = self._resourceNormalKey()
        quill = scene.resources.quill(self.resourcesName(), key)
        return quill.bold()

    @checked
    def setTextBold(self : Self, bold: bool | None | NoChange) -> None:
        if isinstance(bold, NoChange):
            return
        if not hasattr(self, "_text_bold"):
            logger().error("This item does not support text bold overrides.")
            return
        self._text_bold = bold
        self._updateQuill()
        if isinstance(self, PropertiesMixin):
            self.properties["Text Bold"].notify()

    def hasTextItalic(self : Self) -> bool:
        return hasattr(self, "_text_italic")

    def textItalic(self : Self) -> bool | None:
        return self._text_italic if hasattr(self, "_text_italic") else None

    def themeTextItalic(
        self : Self,
        view : DiagramView | None = None
    ) -> bool | None:
        from .. import ItemNamesMixin
        from . import ItemPresentationMixin
        if not isinstance(self, ItemPresentationMixin) \
        or not isinstance(self, ItemNamesMixin):
            raise TypeError("Bad host")
        if (scene := self._defaultScene(view)) is None:
            return None
        key = self._resourceNormalKey()
        quill = scene.resources.quill(self.resourcesName(), key)
        return quill.italic()

    @checked
    def setTextItalic(self : Self, italic: bool | None | NoChange) -> None:
        if isinstance(italic, NoChange):
            return
        if not hasattr(self, "_text_italic"):
            logger().error("This item does not support text italic overrides.")
            return
        self._text_italic = italic
        self._updateQuill()
        if isinstance(self, PropertiesMixin):
            self.properties["Text Italic"].notify()

    def hasTextUnderline(self : Self) -> bool:
        return hasattr(self, "_text_underline")

    def textUnderline(self : Self) -> bool | None:
        return self._text_underline if hasattr(self, "_text_underline") else None

    def themeTextUnderline(
        self : Self,
        view : DiagramView | None = None
    ) -> bool | None:
        from .. import ItemNamesMixin
        from . import ItemPresentationMixin
        if not isinstance(self, ItemPresentationMixin) \
        or not isinstance(self, ItemNamesMixin):
            raise TypeError("Bad host")
        if (scene := self._defaultScene(view)) is None:
            return None
        key = self._resourceNormalKey()
        quill = scene.resources.quill(self.resourcesName(), key)
        return quill.underline()

    @checked
    def setTextUnderline(self : Self, underline: bool | None | NoChange) -> None:
        if isinstance(underline, NoChange):
            return
        if not hasattr(self, "_text_underline"):
            logger().error("This item does not support text underline overrides.")
            return
        self._text_underline = underline
        self._updateQuill()
        if isinstance(self, PropertiesMixin):
            self.properties["Text Underline"].notify()

    # helpers

    @withScene
    def _updateQuill(self : Self) -> None:
        raise NotImplementedError("Not wired!")

    @withScene
    def _updateQuillFast(self : Self, scene : DiagramScene) -> None:
        from .. import ItemNamesMixin
        from . import ItemPresentationMixin
        if not isinstance(self, SetQuillProtocol) \
        or not isinstance(self, ItemNamesMixin) \
        or not isinstance(self, ItemPresentationMixin):
            raise TypeError("Bad host")
        quill = scene.resources.quill(
            self.resourcesName(), self._resourceKey()
        )
        self.setQuill(quill)

    @withScene
    def _updateQuillSlow(self : Self, scene : DiagramScene) -> None:
        from .. import ItemNamesMixin
        from . import ItemPresentationMixin
        if not isinstance(self, QGraphicsItem) \
        or not isinstance(self, SetQuillProtocol) \
        or not isinstance(self, ItemNamesMixin) \
        or not isinstance(self, ItemPresentationMixin):
            raise TypeError("Bad host")
        quill = scene.resources.quill(
            self.resourcesName(), self._resourceKey()
        )
        unselected = not self.isSelected()
        override_color = self._text_color if unselected \
            and hasattr(self, "_text_color") and self._text_color is not None \
            else None
        override_font = self._text_font if unselected \
            and hasattr(self, "_text_font") and self._text_font is not None \
            else None
        override_size = self._text_size if unselected \
            and hasattr(self, "_text_size") and self._text_size is not None \
            else None
        override_bold = self._text_bold if unselected \
            and hasattr(self, "_text_bold") and self._text_bold is not None \
            else None
        override_italic = self._text_italic if unselected \
            and hasattr(self, "_text_italic") and self._text_italic is not None \
            else None
        override_underline = self._text_underline if unselected \
            and hasattr(self, "_text_underline") and self._text_underline is not None \
            else None
        quill = Quill(quill)
        if override_color     is not None: quill.setColor(override_color)
        if override_font      is not None: quill.setFont(override_font)
        if override_size      is not None: quill.setSize(override_size)
        if override_bold      is not None: quill.setBold(override_bold)
        if override_italic    is not None: quill.setItalic(override_italic)
        if override_underline is not None: quill.setUnderline(override_underline)
        self.setQuill(quill)
