from typing      import Self, Protocol, TypeAlias
from dataclasses import dataclass

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QColor

from .......core.types import Default, NoChange, NO_CHANGE

from .. import CmdSceneItems

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .....scenes.drawing    import DrawingScene
    from .....items             import ItemMixin
    from .....items.mixin.line  import ItemLineMixin
    from .....items.mixin.fill  import ItemFillMixin
    from .....items.mixin.quill import ItemQuillMixin


class CmdEditAppearance(CmdSceneItems):
    class OnGeometryChangeProtocol(Protocol):
        def onGeometryChange(self : Self) -> None: ...

    ItemType : TypeAlias = """
        QGraphicsItem            |
        OnGeometryChangeProtocol |
        ItemLineMixin            |
        ItemFillMixin            |
        ItemQuillMixin
    """

    @dataclass
    class ItemBefore:
        line_color     : QColor        | Default
        line_width     : float         | Default
        line_style     : Qt.PenStyle   | Default
        fill_color     : QColor        | Default
        fill_style     : Qt.BrushStyle | Default
        text_color     : QColor        | Default
        text_family    : str           | Default
        text_size      : float         | Default
        text_bold      : bool          | Default
        text_italic    : bool          | Default
        text_underline : bool          | Default

    @dataclass
    class ItemAfter:
        line_color     : QColor        | Default | NoChange
        line_width     : float         | Default | NoChange
        line_style     : Qt.PenStyle   | Default | NoChange
        fill_color     : QColor        | Default | NoChange
        fill_style     : Qt.BrushStyle | Default | NoChange
        text_color     : QColor        | Default | NoChange
        text_family    : str           | Default | NoChange
        text_size      : float         | Default | NoChange
        text_bold      : bool          | Default | NoChange
        text_italic    : bool          | Default | NoChange
        text_underline : bool          | Default | NoChange

    _items  : list[ItemType]
    _before : dict["ItemMixin", ItemBefore]
    _after  : ItemAfter

    def __init__(
        self           : Self,
        scene          : "DrawingScene",
        items          : list[ItemType],
        line_color     : QColor        | Default | NoChange,
        line_width     : float         | Default | NoChange,
        line_style     : Qt.PenStyle   | Default | NoChange,
        fill_color     : QColor        | Default | NoChange,
        fill_style     : Qt.BrushStyle | Default | NoChange,
        text_color     : QColor        | Default | NoChange,
        text_family    : str           | Default | NoChange,
        text_size      : float         | Default | NoChange,
        text_bold      : bool          | Default | NoChange,
        text_italic    : bool          | Default | NoChange,
        text_underline : bool          | Default | NoChange
    ):
        super().__init__(scene, items)
        self._before = {}
        for item in items:
            self._before[item] = self.ItemBefore(
                item.lineColor(),
                item.lineWidth(),
                item.lineStyle(),
                item.fillColor(),
                item.fillStyle(),
                item.quillColor(),
                item.quillFamily(),
                item.quillSize(),
                item.quillBold(),
                item.quillItalic(),
                item.quillUnderline()
            )
        self._after = self.ItemAfter(
            line_color,
            line_width,
            line_style,
            fill_color,
            fill_style,
            text_color,
            text_family,
            text_size,
            text_bold,
            text_italic,
            text_underline
        )

    def redo(self : Self) -> None:
        for item in self._items:
            if self._after.line_color is not NO_CHANGE:
                item.setLineColor(self._after.line_color)
            if self._after.line_width is not NO_CHANGE:
                item.setLineWidth(self._after.line_width)
            if self._after.line_style is not NO_CHANGE:
                item.setLineStyle(self._after.line_style)
            if self._after.fill_color is not NO_CHANGE:
                item.setFillColor(self._after.fill_color)
            if self._after.fill_style is not NO_CHANGE:
                item.setFillStyle(self._after.fill_style)
            if self._after.text_color is not NO_CHANGE:
                item.setQuillColor(self._after.text_color)
            if self._after.text_family is not NO_CHANGE:
                item.setQuillFamily(self._after.text_family)
            if self._after.text_size is not NO_CHANGE:
                item.setQuillSize(self._after.text_size)
            if self._after.text_bold is not NO_CHANGE:
                item.setQuillBold(self._after.text_bold)
            if self._after.text_italic is not NO_CHANGE:
                item.setQuillItalic(self._after.text_italic)
            if self._after.text_underline is not NO_CHANGE:
                item.setQuillUnderline(self._after.text_underline)
            item.onGeometryChange()
            item.update()

    def undo(self : Self) -> None:
        for item in self._items:
            if self._after[item].line_color is not NO_CHANGE:
                item.setLineColor(self._before[item].line_color)
            if self._after[item].line_width is not NO_CHANGE:
                item.setLineWidth(self._before[item].line_width)
            if self._after[item].line_style is not NO_CHANGE:
                item.setLineStyle(self._before[item].line_style)
            if self._after[item].fill_color is not NO_CHANGE:
                item.setFillColor(self._before[item].fill_color)
            if self._after[item].fill_style is not NO_CHANGE:
                item.setFillStyle(self._before[item].fill_style)
            if self._after[item].text_color is not NO_CHANGE:
                item.setQuillColor(self._before[item].text_color)
            if self._after[item].text_family is not NO_CHANGE:
                item.setQuillFamily(self._before[item].text_family)
            if self._after[item].text_size is not NO_CHANGE:
                item.setQuillSize(self._before[item].text_size)
            if self._after[item].text_bold is not NO_CHANGE:
                item.setQuillBold(self._before[item].text_bold)
            if self._after[item].text_italic is not NO_CHANGE:
                item.setQuillItalic(self._before[item].text_italic)
            if self._after[item].text_underline is not NO_CHANGE:
                item.setQuillUnderline(self._before[item].text_underline)
            item.onGeometryChange()
            item.update()
