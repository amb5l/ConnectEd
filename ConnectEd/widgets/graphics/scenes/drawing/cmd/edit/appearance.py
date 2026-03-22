from typing      import Self, Any, Protocol, TypeAlias
from dataclasses import dataclass

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QColor

from .......core.types import Default, NoChange, NO_CHANGE

from .....items.mixin import ItemMixin

from .....items.mixin.line  import ItemLineMixin
from .....items.mixin.fill  import ItemFillMixin
from .....items.mixin.quill import ItemQuillMixin

from .. import CmdSceneItems

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .....scenes.drawing    import DrawingScene

class CmdEditAppearance(CmdSceneItems):
    class OnGeometryChangeProtocol(Protocol):
        def onGeometryChange(self : Self) -> None: ...

    ItemType : TypeAlias = \
        QGraphicsItem            | \
        OnGeometryChangeProtocol | \
        ItemLineMixin            | \
        ItemFillMixin            | \
        ItemQuillMixin

    @dataclass
    class ItemBefore:
        """
        Snapshot of item properties before the change.
        None means item does not have the property.
        """
        line_color     : QColor        | Default | None
        line_width     : float         | Default | None
        line_style     : Qt.PenStyle   | Default | None
        fill_color     : QColor        | Default | None
        fill_style     : Qt.BrushStyle | Default | None
        text_color     : QColor        | Default | None
        text_family    : str           | Default | None
        text_size      : float         | Default | None
        text_bold      : bool          | Default | None
        text_italic    : bool          | Default | None
        text_underline : bool          | Default | None

    @dataclass
    class ItemAfter:
        """
        New values for item properties after the change.
        None means item does not have the property.
        """
        line_color     : QColor        | Default | NoChange | None
        line_width     : float         | Default | NoChange | None
        line_style     : Qt.PenStyle   | Default | NoChange | None
        fill_color     : QColor        | Default | NoChange | None
        fill_style     : Qt.BrushStyle | Default | NoChange | None
        text_color     : QColor        | Default | NoChange | None
        text_family    : str           | Default | NoChange | None
        text_size      : float         | Default | NoChange | None
        text_bold      : bool          | Default | NoChange | None
        text_italic    : bool          | Default | NoChange | None
        text_underline : bool          | Default | NoChange | None

    _items  : list[ItemType]
    _before : dict[ItemMixin, ItemBefore]
    _after  : ItemAfter

    def __init__(
        self           : Self,
        scene          : "DrawingScene",
        items          : list[ItemType],
        line_color     : QColor        | Default | NoChange | None,
        line_width     : float         | Default | NoChange | None,
        line_style     : Qt.PenStyle   | Default | NoChange | None,
        fill_color     : QColor        | Default | NoChange | None,
        fill_style     : Qt.BrushStyle | Default | NoChange | None,
        text_color     : QColor        | Default | NoChange | None,
        text_family    : str           | Default | NoChange | None,
        text_size      : float         | Default | NoChange | None,
        text_bold      : bool          | Default | NoChange | None,
        text_italic    : bool          | Default | NoChange | None,
        text_underline : bool          | Default | NoChange | None
    ):
        super().__init__(scene, items)
        self._before = {}
        for item in items:
            has_line = isinstance(item, ItemLineMixin)
            has_fill = isinstance(item, ItemFillMixin)
            has_text = isinstance(item, ItemQuillMixin)
            self._before[item] = self.ItemBefore(
                item.lineColor()      if has_line else None,
                item.lineWidth()      if has_line else None,
                item.lineStyle()      if has_line else None,
                item.fillColor()      if has_fill else None,
                item.fillStyle()      if has_fill else None,
                item.quillColor()     if has_text else None,
                item.quillFamily()    if has_text else None,
                item.quillSize()      if has_text else None,
                item.quillBold()      if has_text else None,
                item.quillItalic()    if has_text else None,
                item.quillUnderline() if has_text else None
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
            if self._applicable(self._after.line_color):
                item.setLineColor(self._after.line_color)
            if self._applicable(self._after.line_width):
                item.setLineWidth(self._after.line_width)
            if self._applicable(self._after.line_style):
                item.setLineStyle(self._after.line_style)
            if self._applicable(self._after.fill_color):
                item.setFillColor(self._after.fill_color)
            if self._applicable(self._after.fill_style):
                item.setFillStyle(self._after.fill_style)
            if self._applicable(self._after.text_color):
                item.setQuillColor(self._after.text_color)
            if self._applicable(self._after.text_family):
                item.setQuillFamily(self._after.text_family)
            if self._applicable(self._after.text_size):
                item.setQuillSize(self._after.text_size)
            if self._applicable(self._after.text_bold):
                item.setQuillBold(self._after.text_bold)
            if self._applicable(self._after.text_italic):
                item.setQuillItalic(self._after.text_italic)
            if self._applicable(self._after.text_underline):
                item.setQuillUnderline(self._after.text_underline)
            item.onGeometryChange()
            item.update()

    def undo(self : Self) -> None:
        for item in self._items:
            if self._applicable(self._after[item].line_color):
                item.setLineColor(self._before[item].line_color)
            if self._applicable(self._after[item].line_width):
                item.setLineWidth(self._before[item].line_width)
            if self._applicable(self._after[item].line_style):
                item.setLineStyle(self._before[item].line_style)
            if self._applicable(self._after[item].fill_color):
                item.setFillColor(self._before[item].fill_color)
            if self._applicable(self._after[item].fill_style):
                item.setFillStyle(self._before[item].fill_style)
            if self._applicable(self._after[item].text_color):
                item.setQuillColor(self._before[item].text_color)
            if self._applicable(self._after[item].text_family):
                item.setQuillFamily(self._before[item].text_family)
            if self._applicable(self._after[item].text_size):
                item.setQuillSize(self._before[item].text_size)
            if self._applicable(self._after[item].text_bold):
                item.setQuillBold(self._before[item].text_bold)
            if self._applicable(self._after[item].text_italic):
                item.setQuillItalic(self._before[item].text_italic)
            if self._applicable(self._after[item].text_underline):
                item.setQuillUnderline(self._before[item].text_underline)
            item.onGeometryChange()
            item.update()

    def _applicable(self : Self, param : Any) -> bool:
        return param is not None and param is not NO_CHANGE
