from __future__ import annotations

from typing import Self, TYPE_CHECKING

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QColor

from ......core.check import checked
from ......core.types import DataKind

from ....properties import InherentProperty

from ....scenes import withScene

from ...protocols import OnSceneChangedProtocol

from .line   import ItemPresentationLineMixin  # noqa: E402
from .fill   import ItemPresentationFillMixin  # noqa: E402
from .text   import ItemPresentationTextMixin  # noqa: E402


if TYPE_CHECKING:
    from ....views.diagram  import DiagramView
    from ....scenes.diagram import DiagramScene


class ItemPresentationMixin(
    ItemPresentationLineMixin,
    ItemPresentationFillMixin,
    ItemPresentationTextMixin
):
    # class attributes
    _PROPERTIES_LINE = {
        "Line Color" : InherentProperty["ItemPresentationMixin"](
            kind    = DataKind.COLOR,
            worthy  = lambda self: self.lineColor() is not None,
            getter  = lambda self: self.lineColor(),
            setter  = lambda self, value: self.setLineColor(value),
            default = lambda self: self.defaultLineColor()
        ),
        "Line Width" : InherentProperty["ItemPresentationMixin"](
            kind    = DataKind.PEN_WIDTH,
            worthy  = lambda self: self.lineWidth() is not None,
            getter  = lambda self: self.lineWidth(),
            setter  = lambda self, value: self.setLineWidth(value),
            default = lambda self: self.defaultLineWidth()
        ),
        "Line Style" : InherentProperty["ItemPresentationMixin"](
            kind    = DataKind.PEN_STYLE,
            worthy  = lambda self: self.lineStyle() is not None,
            getter  = lambda self: self.lineStyle(),
            setter  = lambda self, value: self.setLineStyle(value),
            default = lambda self: self.defaultLineStyle()
        )
    }
    _PROPERTIES_FILL = {
        "Fill Color" : InherentProperty["ItemPresentationMixin"](
            kind    = DataKind.COLOR,
            worthy  = lambda self: self.fillColor() is not None,
            getter  = lambda self: self.fillColor(),
            setter  = lambda self, value: self.setFillColor(value),
            default = lambda self: self.defaultFillColor()
        ),
        "Fill Style" : InherentProperty["ItemPresentationMixin"](
            kind    = DataKind.BRUSH_STYLE,
            worthy  = lambda self: self.fillStyle() is not None,
            getter  = lambda self: self.fillStyle(),
            setter  = lambda self, value: self.setFillStyle(value),
            default = lambda self: self.defaultFillStyle()
        )
    }
    _PROPERTIES_TEXT = {
        "Text Color" : InherentProperty["ItemPresentationMixin"](
            kind    = DataKind.COLOR,
            worthy  = lambda self: self.textColor() is not None,
            getter  = lambda self: self.textColor(),
            setter  = lambda self, value: self.setTextColor(value),
            default = lambda self: self.defaultTextColor()
        ),
        "Text Font" : InherentProperty["ItemPresentationMixin"](
            kind    = DataKind.FONT_FAMILY,
            worthy  = lambda self: self.textFont() is not None,
            getter  = lambda self: self.textFont(),
            setter  = lambda self, value: self.setTextFont(value),
            default = lambda self: self.defaultTextFont()
        ),
        "Text Size" : InherentProperty["ItemPresentationMixin"](
            kind    = DataKind.FONT_SIZE,
            worthy  = lambda self: self.textSize() is not None,
            getter  = lambda self: self.textSize(),
            setter  = lambda self, value: self.setTextSize(value),
            default = lambda self: self.defaultTextSize()
        ),
        "Text Bold" : InherentProperty["ItemPresentationMixin"](
            kind    = DataKind.FONT_BOOL,
            worthy  = lambda self: self.textBold() is not None,
            getter  = lambda self: self.textBold(),
            setter  = lambda self, value: self.setTextBold(value),
            default = lambda self: self.defaultTextBold()
        ),
        "Text Italic" : InherentProperty["ItemPresentationMixin"](
            kind    = DataKind.FONT_BOOL,
            worthy  = lambda self: self.textItalic() is not None,
            getter  = lambda self: self.textItalic(),
            setter  = lambda self, value: self.setTextItalic(value),
            default = lambda self: self.defaultTextItalic()
        ),
        "Text Underline" : InherentProperty["ItemPresentationMixin"](
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
    def initPresentation(self : Self) -> None:
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

    def _resourceKey(self : Self) -> bool | tuple:
        """Theme lookup key for pen, brush and quill. Override in subclass."""
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        return self.isSelected()

    def _resourceKeyDefault(self : Self) -> bool | tuple:
        """Default theme lookup key (non-selected, normal state)."""
        return False

    def onSettingsChanged(self : Self) -> None:
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        if isinstance(self, OnSceneChangedProtocol):
            self.onSceneChanged(self.scene())

    @withScene
    def onSceneChanged(self : Self, scene : DiagramScene) -> None:
        if hasattr(self, "setPen"):
            self._updatePen(scene)
        if hasattr(self, "setBrush"):
            self._updateBrush(scene)
        if hasattr(self, "setQuill"):
            self._updateQuill(scene)
        if hasattr(self, "_updateGraphics"):
            self._updateGraphics(scene)

    def _updateGraphics(self : Self, _scene : DiagramScene) -> None:
        """Optional hook; subclasses (pins, nodes, …) override when needed."""
        pass

    def _defaultScene(
        self : Self,
        view : DiagramView | None = None
    ) -> DiagramScene | None:
        from ....scenes.diagram import DiagramScene
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        scene = self.scene()
        if scene is None and view is not None:
            scene = view.scene()
        return scene if isinstance(scene, DiagramScene) else None
