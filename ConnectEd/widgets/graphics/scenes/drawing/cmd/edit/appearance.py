from __future__ import annotations

from typing      import Self
from dataclasses import dataclass

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QColor

from .......core.check import checked
from .......core.types import NoChange, NO_CHANGE

from .....items.mixin import ItemMixin

from .. import CmdSceneItems

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .....items import ItemType
    from .....scenes.drawing import DrawingScene

class CmdEditAppearance(CmdSceneItems):
    @dataclass
    class ItemBefore:
        """
        Snapshot of item properties before the change.
        NO_CHANGE means item does not have the property.
        """
        line_color     : QColor        | None | NoChange
        line_width     : float         | None | NoChange
        line_style     : Qt.PenStyle   | None | NoChange
        fill_color     : QColor        | None | NoChange
        fill_style     : Qt.BrushStyle | None | NoChange
        text_color     : QColor        | None | NoChange
        text_font      : str           | None | NoChange
        text_size      : float         | None | NoChange
        text_bold      : bool          | None | NoChange
        text_italic    : bool          | None | NoChange
        text_underline : bool          | None | NoChange

    @dataclass
    class ItemAfter:
        """
        New values for item properties after the change.
        """
        line_color     : QColor        | None | NoChange
        line_width     : float         | None | NoChange
        line_style     : Qt.PenStyle   | None | NoChange
        fill_color     : QColor        | None | NoChange
        fill_style     : Qt.BrushStyle | None | NoChange
        text_color     : QColor        | None | NoChange
        text_font      : str           | None | NoChange
        text_size      : float         | None | NoChange
        text_bold      : bool          | None | NoChange
        text_italic    : bool          | None | NoChange
        text_underline : bool          | None | NoChange

    _items  : list[ItemType]
    _before : dict[ItemMixin, ItemBefore]
    _after  : ItemAfter

    @checked
    def __init__(
        self           : Self,
        scene          : DrawingScene,
        items          : list[ItemType],
        line_color     : QColor        | None | NoChange = NO_CHANGE,
        line_width     : float         | None | NoChange = NO_CHANGE,
        line_style     : Qt.PenStyle   | None | NoChange = NO_CHANGE,
        fill_color     : QColor        | None | NoChange = NO_CHANGE,
        fill_style     : Qt.BrushStyle | None | NoChange = NO_CHANGE,
        text_color     : QColor        | None | NoChange = NO_CHANGE,
        text_font      : str           | None | NoChange = NO_CHANGE,
        text_size      : float         | None | NoChange = NO_CHANGE,
        text_bold      : bool          | None | NoChange = NO_CHANGE,
        text_italic    : bool          | None | NoChange = NO_CHANGE,
        text_underline : bool          | None | NoChange = NO_CHANGE
    ) -> None:
        super().__init__(scene, items)
        self._before = {}
        for item in items:
            self._before[item] = self.ItemBefore(
                item.lineColor()      if item.hasLineColor()     else NO_CHANGE,
                item.lineWidth()      if item.hasLineWidth()     else NO_CHANGE,
                item.lineStyle()      if item.hasLineStyle()     else NO_CHANGE,
                item.fillColor()      if item.hasFillColor()     else NO_CHANGE,
                item.fillStyle()      if item.hasFillStyle()     else NO_CHANGE,
                item.textColor()      if item.hasTextColor()     else NO_CHANGE,
                item.textFont()       if item.hasTextFont()      else NO_CHANGE,
                item.textSize()       if item.hasTextSize()      else NO_CHANGE,
                item.textBold()       if item.hasTextBold()      else NO_CHANGE,
                item.textItalic()     if item.hasTextItalic()    else NO_CHANGE,
                item.textUnderline()  if item.hasTextUnderline() else NO_CHANGE
            )
        self._after = self.ItemAfter(
            line_color,
            line_width,
            line_style,
            fill_color,
            fill_style,
            text_color,
            text_font,
            text_size,
            text_bold,
            text_italic,
            text_underline
        )

    @checked
    def redo(self : Self) -> None:
        for item in self._items:
            if self._before[item].line_color is not NO_CHANGE:
                item.setLineColor(self._after.line_color)
            if self._before[item].line_width is not NO_CHANGE:
                item.setLineWidth(self._after.line_width)
            if self._before[item].line_style is not NO_CHANGE:
                item.setLineStyle(self._after.line_style)
            if self._before[item].fill_color is not NO_CHANGE:
                item.setFillColor(self._after.fill_color)
            if self._before[item].fill_style is not NO_CHANGE:
                item.setFillStyle(self._after.fill_style)
            if self._before[item].text_color is not NO_CHANGE:
                item.setTextColor(self._after.text_color)
            if self._before[item].text_font is not NO_CHANGE:
                item.setTextFont(self._after.text_font)
            if self._before[item].text_size is not NO_CHANGE:
                item.setTextSize(self._after.text_size)
            if self._before[item].text_bold is not NO_CHANGE:
                item.setTextBold(self._after.text_bold)
            if self._before[item].text_italic is not NO_CHANGE:
                item.setTextItalic(self._after.text_italic)
            if self._before[item].text_underline is not NO_CHANGE:
                item.setTextUnderline(self._after.text_underline)
            if hasattr(item, "onGeometryChanged"):
                item.onGeometryChanged()
            item.update()

    @checked
    def undo(self : Self) -> None:
        for item in self._items:
            if self._before[item].line_color is not NO_CHANGE:
                item.setLineColor(self._before[item].line_color)
            if self._before[item].line_width is not NO_CHANGE:
                item.setLineWidth(self._before[item].line_width)
            if self._before[item].line_style is not NO_CHANGE:
                item.setLineStyle(self._before[item].line_style)
            if self._before[item].fill_color is not NO_CHANGE:
                item.setFillColor(self._before[item].fill_color)
            if self._before[item].fill_style is not NO_CHANGE:
                item.setFillStyle(self._before[item].fill_style)
            if self._before[item].text_color is not NO_CHANGE:
                item.setTextColor(self._before[item].text_color)
            if self._before[item].text_font is not NO_CHANGE:
                item.setTextFont(self._before[item].text_font)
            if self._before[item].text_size is not NO_CHANGE:
                item.setTextSize(self._before[item].text_size)
            if self._before[item].text_bold is not NO_CHANGE:
                item.setTextBold(self._before[item].text_bold)
            if self._before[item].text_italic is not NO_CHANGE:
                item.setTextItalic(self._before[item].text_italic)
            if self._before[item].text_underline is not NO_CHANGE:
                item.setTextUnderline(self._before[item].text_underline)
            if hasattr(item, "onGeometryChanged"):
                item.onGeometryChanged()
            item.update()
