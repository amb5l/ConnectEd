from typing import Self, Protocol

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QColor, QPen, QBrush

from .....app import logger

from .....core.types import DataKind, NoChange, NO_CHANGE

from ...scenes import withScene
from ...quill  import Quill

from ...properties import InherentProperty

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...scenes.drawing import DrawingScene
    from . import ItemNamesMixin


class PenItemProtocol(Protocol):
    def setPen(self, pen: QPen) -> None: ...


class BrushItemProtocol(Protocol):
    def setBrush(self, brush: QBrush) -> None: ...


class TextItemProtocol(Protocol):
    def setQuill(self, quill: Quill) -> None: ...


class ItemPresentationMixin:
    # class attributes
    _PROPERTIES_LINE = {
        "Line Color" : InherentProperty(
            kind    = DataKind.COLOR,
            worthy  = lambda self: self.lineColor() is not None,
            getter  = lambda self: self.lineColor(),
            setter  = lambda self, value: self.setLineColor(value),
            default = lambda self: self.defaultLineColor()
        ),
        "Line Width" : InherentProperty(
            kind    = DataKind.PEN_WIDTH,
            worthy  = lambda self: self.lineWidth() is not None,
            getter  = lambda self: self.lineWidth(),
            setter  = lambda self, value: self.setLineWidth(value),
            default = lambda self: self.defaultLineWidth()
        ),
        "Line Style" : InherentProperty(
            kind    = DataKind.PEN_STYLE,
            worthy  = lambda self: self.lineStyle() is not None,
            getter  = lambda self: self.lineStyle(),
            setter  = lambda self, value: self.setLineStyle(value),
            default = lambda self: self.defaultLineStyle()
        )
    }
    _PROPERTIES_FILL = {
        "Fill Color" : InherentProperty(
            kind    = DataKind.COLOR,
            worthy  = lambda self: self.fillColor() is not None,
            getter  = lambda self: self.fillColor(),
            setter  = lambda self, value: self.setFillColor(value),
            default = lambda self: self.defaultFillColor()
        ),
        "Fill Style" : InherentProperty(
            kind    = DataKind.BRUSH_STYLE,
            worthy  = lambda self: self.fillStyle() is not None,
            getter  = lambda self: self.fillStyle(),
            setter  = lambda self, value: self.setFillStyle(value),
            default = lambda self: self.defaultFillStyle()
        )
    }
    _PROPERTIES_TEXT = {
        "Text Color" : InherentProperty(
            kind    = DataKind.COLOR,
            worthy  = lambda self: self.textColor() is not None,
            getter  = lambda self: self.textColor(),
            setter  = lambda self, value: self.setTextColor(value),
            default = lambda self: self.defaultTextColor()
        ),
        "Text Font" : InherentProperty(
            kind    = DataKind.FONT_FAMILY,
            worthy  = lambda self: self.textFont() is not None,
            getter  = lambda self: self.textFont(),
            setter  = lambda self, value: self.setTextFont(value),
            default = lambda self: self.defaultTextFont()
        ),
        "Text Size" : InherentProperty(
            kind    = DataKind.FONT_SIZE,
            worthy  = lambda self: self.textSize() is not None,
            getter  = lambda self: self.textSize(),
            setter  = lambda self, value: self.setTextSize(value),
            default = lambda self: self.defaultTextSize()
        ),
        "Text Bold" : InherentProperty(
            kind    = DataKind.FONT_BOOL,
            worthy  = lambda self: self.textBold() is not None,
            getter  = lambda self: self.textBold(),
            setter  = lambda self, value: self.setTextBold(value),
            default = lambda self: self.defaultTextBold()
        ),
        "Text Italic" : InherentProperty(
            kind    = DataKind.FONT_BOOL,
            worthy  = lambda self: self.textItalic() is not None,
            getter  = lambda self: self.textItalic(),
            setter  = lambda self, value: self.setTextItalic(value),
            default = lambda self: self.defaultTextItalic()
        ),
        "Text Underline" : InherentProperty(
            kind    = DataKind.FONT_BOOL,
            worthy  = lambda self: self.textUnderline() is not None,
            getter  = lambda self: self.textUnderline(),
            setter  = lambda self, value: self.setTextUnderline(value),
            default = lambda self: self.defaultTextUnderline()
        )
    }

    # to enable item specific overrides,
    #  declare one or more of the following = None
    # non-existent attributes are ignored and will not be offered in dialogs
    _line_color     : QColor        | None
    _line_width     : float         | None
    _line_style     : Qt.PenStyle   | None
    _fill_color     : QColor        | None
    _fill_style     : Qt.BrushStyle | None
    _text_color     : QColor        | None
    _text_font      : str           | None
    _text_size      : float         | None
    _text_bold      : bool          | None
    _text_italic    : bool          | None
    _text_underline : bool          | None

    def initPresentation(self : Self) -> None:
        from .select import ItemSelectMixin
        if not isinstance(self, ItemSelectMixin):
            raise TypeError("This item does not support the ItemSelectionMixin")
        # wire update methods
        if hasattr(self, "setPen"):
            self._updatePen = self._updatePenFast
            if hasattr(self, "_line_color") \
            or hasattr(self, "_line_width") \
            or hasattr(self, "_line_style"):
                self._updatePen = self._updatePenSlow
        if hasattr(self, "setBrush"):
            self._updateBrush = self._updateBrushFast
            if hasattr(self, "_fill_color") \
            or hasattr(self, "_fill_style"):
                self._updateBrush = self._updateBrushSlow
        if hasattr(self, "setQuill"):
            self._updateQuill = self._updateQuillFast
            if hasattr(self, "_text_color") \
            or hasattr(self, "_text_font") \
            or hasattr(self, "_text_size") \
            or hasattr(self, "_text_bold") \
            or hasattr(self, "_text_italic") \
            or hasattr(self, "_text_underline"):
                self._updateQuill = self._updateQuillSlow

    def onSettingsChanged(self : Self) -> None:
        self.onSceneChanged(self.scene())

    @withScene
    def onSceneChanged(self : Self, scene : "DrawingScene") -> None:
        if hasattr(self, "setPen"):
            self._updatePen(scene)
        if hasattr(self, "setBrush"):
            self._updateBrush(scene)
        if hasattr(self, "setQuill"):
            self._updateQuill(scene)
        if hasattr(self, "_updateGraphics"):
            self._updateGraphics(scene)


    # line methods

    def hasLine(self) -> bool:
        return self.hasLineColor() or self.hasLineWidth() or self.hasLineStyle()

    def hasLineColor(self) -> bool:
        return hasattr(self, "_line_color")

    def lineColor(self) -> QColor | None:
        return self._line_color if hasattr(self, "_line_color") else None

    def defaultLineColor(self) -> QColor | None:
        if (scene := self.scene()) is None: return None
        key = self._penKeyDefault()
        pen = scene.resources.pen(self.resourcesName(), key)
        return pen.color()

    def setLineColor(self, color: QColor | None | NoChange) -> None:
        if color is NO_CHANGE:
            return
        if not hasattr(self, "_line_color"):
            logger().error("This item does not support line color overrides.")
            return
        self._line_color = color
        self._updatePen()

    def hasLineWidth(self) -> bool:
        return hasattr(self, "_line_width")

    def lineWidth(self) -> float | None:
        return self._line_width if hasattr(self, "_line_width") else None

    def defaultLineWidth(self) -> float | None:
        if (scene := self.scene()) is None: return None
        key = self._penKeyDefault()
        pen = scene.resources.pen(self.resourcesName(), key)
        return pen.widthF()

    def setLineWidth(self, width: float | None | NoChange) -> None:
        if width is NO_CHANGE:
            return
        if not hasattr(self, "_line_width"):
            logger().error("This item does not support line width overrides.")
            return
        self._line_width = width
        self._updatePen()

    def hasLineStyle(self) -> bool:
        return hasattr(self, "_line_style")

    def lineStyle(self) -> Qt.PenStyle | None:
        return self._line_style if hasattr(self, "_line_style") else None

    def defaultLineStyle(self) -> Qt.PenStyle | None:
        if (scene := self.scene()) is None: return None
        key = self._penKeyDefault()
        pen = scene.resources.pen(self.resourcesName(), key)
        return pen.style()

    def setLineStyle(self, style: Qt.PenStyle | None | NoChange) -> None:
        if style is NO_CHANGE:
            return
        if not hasattr(self, "_line_style"):
            logger().error("This item does not support line style overrides.")
            return
        self._line_style = style
        self._updatePen()

    # fill methods

    def hasFill(self) -> bool:
        return self.hasFillColor() or self.hasFillStyle()

    def hasFillColor(self) -> bool:
        return hasattr(self, "_fill_color")

    def fillColor(self) -> QColor | None:
        return self._fill_color if hasattr(self, "_fill_color") else None

    def defaultFillColor(self) -> QColor | None:
        if (scene := self.scene()) is None: return None
        key = self._brushKeyDefault()
        brush = scene.resources.brush(self.resourcesName(), key)
        return brush.color()

    def setFillColor(self, color: QColor | None | NoChange) -> None:
        if color is NO_CHANGE:
            return
        if not hasattr(self, "_fill_color"):
            logger().error("This item does not support fill color overrides.")
            return
        self._fill_color = color
        self._updateBrush()

    def hasFillStyle(self) -> bool:
        return hasattr(self, "_fill_style")

    def fillStyle(self) -> Qt.BrushStyle | None:
        return self._fill_style if hasattr(self, "_fill_style") else None

    def defaultFillStyle(self) -> Qt.BrushStyle | None:
        if (scene := self.scene()) is None: return None
        key = self._brushKeyDefault()
        brush = scene.resources.brush(self.resourcesName(), key)
        return brush.style()

    def setFillStyle(self, style: Qt.BrushStyle | None | NoChange) -> None:
        if style is NO_CHANGE:
            return
        if not hasattr(self, "_fill_style"):
            logger().error("This item does not support fill style overrides.")
            return
        self._fill_style = style
        self._updateBrush()

    # text methods

    def hasText(self) -> bool:
        return (
               self.hasTextColor()
            or self.hasTextFont()
            or self.hasTextSize()
            or self.hasTextBold()
            or self.hasTextItalic()
            or self.hasTextUnderline()
        )

    def hasTextColor(self) -> bool:
        return hasattr(self, "_text_color")

    def textColor(self) -> QColor | None:
        return self._text_color if hasattr(self, "_text_color") else None

    def defaultTextColor(self) -> QColor | None:
        if (scene := self.scene()) is None: return None
        key = self._quillKeyDefault()
        quill = scene.resources.quill(self.resourcesName(), key)
        return quill.color()

    def setTextColor(self, color: QColor | None | NoChange) -> None:
        if color is NO_CHANGE:
            return
        if not hasattr(self, "_text_color"):
            logger().error("This item does not support text color overrides.")
            return
        self._text_color = color
        self._updateQuill()

    def hasTextFont(self) -> bool:
        return hasattr(self, "_text_font")

    def textFont(self) -> str | None:
        return self._text_font if hasattr(self, "_text_font") else None

    def defaultTextFont(self) -> str | None:
        if (scene := self.scene()) is None: return None
        key = self._quillKeyDefault()
        quill = scene.resources.quill(self.resourcesName(), key)
        return quill.font()

    def setTextFont(self, font: str | None | NoChange) -> None:
        if font is NO_CHANGE:
            return
        if not hasattr(self, "_text_font"):
            logger().error("This item does not support text font overrides.")
            return
        self._text_font = font
        self._updateQuill()

    def hasTextSize(self) -> bool:
        return hasattr(self, "_text_size")

    def textSize(self) -> float | None:
        return self._text_size if hasattr(self, "_text_size") else None

    def defaultTextSize(self) -> float | None:
        if (scene := self.scene()) is None: return None
        key = self._quillKeyDefault()
        quill = scene.resources.quill(self.resourcesName(), key)
        return quill.size()

    def setTextSize(self, size: float | None | NoChange) -> None:
        if size is NO_CHANGE:
            return
        if not hasattr(self, "_text_size"):
            logger().error("This item does not support text size overrides.")
            return
        self._text_size = size
        self._updateQuill()

    def hasTextBold(self) -> bool:
        return hasattr(self, "_text_bold")

    def textBold(self) -> bool | None:
        return self._text_bold if hasattr(self, "_text_bold") else None

    def defaultTextBold(self) -> bool | None:
        if (scene := self.scene()) is None: return None
        key = self._quillKeyDefault()
        quill = scene.resources.quill(self.resourcesName(), key)
        return quill.bold()

    def setTextBold(self, bold: bool | None | NoChange) -> None:
        if bold is NO_CHANGE:
            return
        if not hasattr(self, "_text_bold"):
            logger().error("This item does not support text bold overrides.")
            return
        self._text_bold = bold
        self._updateQuill()

    def hasTextItalic(self) -> bool:
        return hasattr(self, "_text_italic")

    def textItalic(self) -> bool | None:
        return self._text_italic if hasattr(self, "_text_italic") else None

    def defaultTextItalic(self) -> bool | None:
        if (scene := self.scene()) is None: return None
        key = self._quillKeyDefault()
        quill = scene.resources.quill(self.resourcesName(), key)
        return quill.italic()

    def setTextItalic(self, italic: bool | None | NoChange) -> None:
        if italic is NO_CHANGE:
            return
        if not hasattr(self, "_text_italic"):
            logger().error("This item does not support text italic overrides.")
            return
        self._text_italic = italic
        self._updateQuill()

    def hasTextUnderline(self) -> bool:
        return hasattr(self, "_text_underline")

    def textUnderline(self) -> bool | None:
        return self._text_underline if hasattr(self, "_text_underline") else None

    def defaultTextUnderline(self) -> bool | None:
        if (scene := self.scene()) is None: return None
        key = self._quillKeyDefault()
        quill = scene.resources.quill(self.resourcesName(), key)
        return quill.underline()

    def setTextUnderline(self, underline: bool | None | NoChange) -> None:
        if underline is NO_CHANGE:
            return
        if not hasattr(self, "_text_underline"):
            logger().error("This item does not support text underline overrides.")
            return
        self._text_underline = underline
        self._updateQuill()

    # helpers

    def _penKey(self : Self | QGraphicsItem) -> bool:
        return self.isSelected()

    def _penKeyDefault(self : Self) -> bool:
        return False

    def _updatePen(self : Self, scene : "DrawingScene") -> None:
        raise NotImplementedError("Not wired!")

    @withScene
    def _updatePenFast(
        self : "Self | ItemNamesMixin | PenItemProtocol",
        scene : "DrawingScene"
    ) -> None:
        pen = scene.resources.pen(self.resourcesName(), self._penKey())
        self.setPen(pen)

    @withScene
    def _updatePenSlow(
        self : "Self | ItemNamesMixin | PenItemProtocol",
        scene : "DrawingScene"
    ) -> None:
        pen = scene.resources.pen(self.resourcesName(), self._penKey())
        override_color = \
            hasattr(self, "_line_color") and not self.isSelected() \
                and self._line_color is not None
        override_width = \
            hasattr(self, "_line_width") and self._line_width is not None
        override_style = \
            hasattr(self, "_line_style") and self._line_style is not None
        if override_color or override_width or override_style:
            pen = QPen(pen)
            if override_color: pen.setColor(self._line_color)
            if override_width: pen.setWidthF(self._line_width)
            if override_style: pen.setStyle(self._line_style)
        self.setPen(pen)

    def _brushKey(self : Self | QGraphicsItem) -> bool:
        return self.isSelected()

    def _brushKeyDefault(self : Self) -> bool:
        return False

    def _updateBrush(self : Self, scene : "DrawingScene") -> None:
        raise NotImplementedError("Not wired!")

    @withScene
    def _updateBrushFast(
        self : "Self | ItemNamesMixin | BrushItemProtocol",
        scene : "DrawingScene"
    ) -> None:
        brush = scene.resources.brush(self.resourcesName(), self._brushKey())
        self.setBrush(brush)

    @withScene
    def _updateBrushSlow(
        self  : "Self | ItemNamesMixin | BrushItemProtocol",
        scene : "DrawingScene"
    ) -> None:
        brush = scene.resources.brush(self.resourcesName(), self._brushKey())
        override_color = \
            hasattr(self, "_fill_color") and not self.isSelected() \
                and self._fill_color is not None
        override_style = \
            hasattr(self, "_fill_style") and self._fill_style is not None
        if override_color or override_style:
            brush = QBrush(brush)
            if override_color: brush.setColor(self._fill_color)
            if override_style: brush.setStyle(self._fill_style)
        self.setBrush(brush)

    def _quillKey(self : Self | QGraphicsItem) -> bool:
        return self.isSelected()

    def _quillKeyDefault(self : Self) -> bool:
        return False

    @withScene
    def _updateQuill(self : Self, scene : "DrawingScene") -> None:
        raise NotImplementedError("Not wired!")

    @withScene
    def _updateQuillFast(
        self : "Self | ItemNamesMixin | TextItemProtocol",
        scene : "DrawingScene"
    ) -> None:
        quill = scene.resources.quill(self.resourcesName(), self._quillKey())
        self.setQuill(quill)

    @withScene
    def _updateQuillSlow(
        self : "Self | ItemNamesMixin | TextItemProtocol",
        scene : "DrawingScene"
    ) -> None:
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
