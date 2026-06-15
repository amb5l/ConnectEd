from typing import Self, Protocol, TypeAlias, TYPE_CHECKING

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QColor, QPen, QBrush

from ......core.check import checked
from ......core.types import DataKind

from ....properties import InherentProperty

from ....scenes import withScene

from ....quill  import Quill

from .line   import ItemPresentationLineMixin  # noqa: E402
from .fill   import ItemPresentationFillMixin  # noqa: E402
from .text   import ItemPresentationTextMixin  # noqa: E402


class PenItemProtocol(Protocol):
    def setPen(self, pen: QPen) -> None: ...


class BrushItemProtocol(Protocol):
    def setBrush(self, brush: QBrush) -> None: ...


class TextItemProtocol(Protocol):
    def setQuill(self, quill: Quill) -> None: ...


if TYPE_CHECKING:
    from ....views.drawing  import DrawingView
    from ....scenes.drawing import DrawingScene
    from .. import ItemNamesMixin
    ItemType = (
        ItemNamesMixin    |
        PenItemProtocol   |
        BrushItemProtocol |
        TextItemProtocol  |
        QGraphicsItem
    )


class ItemPresentationMixin(
    ItemPresentationLineMixin,
    ItemPresentationFillMixin,
    ItemPresentationTextMixin
):
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

    @checked
    def initPresentation(self : "Self | ItemType") -> None:
        from ..select import ItemSelectMixin
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

    def onSettingsChanged(self : "Self | ItemType") -> None:
        self.onSceneChanged(self.scene())

    @withScene
    def onSceneChanged(self : "Self | ItemType", scene : "DrawingScene") -> None:
        if hasattr(self, "setPen"):
            self._updatePen(scene)
        if hasattr(self, "setBrush"):
            self._updateBrush(scene)
        if hasattr(self, "setQuill"):
            self._updateQuill(scene)
        if hasattr(self, "_updateGraphics"):
            self._updateGraphics(scene)

    def _defaultScene(
        self   : "Self | ItemType",
        widget : "DrawingView | None" = None
    ) -> "DrawingScene | None":
        scene : "DrawingScene | None" = self.scene()
        if scene is None:
            scene : "DrawingScene | None" = widget.scene()
        return scene
