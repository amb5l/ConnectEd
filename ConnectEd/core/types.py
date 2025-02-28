"""
Common types and utility classes for the ConnectEd application.

This module provides reusable type definitions and utility classes
used throughout the application, including painting contexts and typed collections.
"""

__all__ = [
    'Action',
    'PainterContext',
    'TypedList',
    'Library'
]

from typing import Type, List, Tuple, Generic, TypeVar, Union, Optional, Iterator

from PyQt6.QtCore    import QObject, Qt
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui     import QAction, QKeySequence, QPainter, QPen, QBrush, QColor

from typing import TYPE_CHECKING
if TYPE_CHECKING: # avoid circular import issues
    from ..widgets import Symbol


class Action(QAction):
    def __init__(
        self      : 'Action',
        parent    : QObject,
        text      : str,
        tooltip   : str,
        shortcut  : QKeySequence | str | None,
        checkable : bool = False,
        checked   : bool = False
    ) -> None:
        super().__init__(parent)
        self.setText(text)
        self.setToolTip(tooltip)
        if shortcut is not None:
            self.setShortcut(shortcut)
        self.setCheckable(checkable)
        if checkable:
            self.setChecked(checked)

class PainterContext:
    """A context object that bundles painter with a reusable pen and brush."""

    painter: QPainter
    pen: QPen
    brush: QBrush

    def __init__(self, widget: QWidget) -> None:
        """Initialize a PainterContext with a widget to paint on.

        Args:
            widget: The QWidget to paint on
        """
        self.painter = QPainter(widget)
        self.pen = QPen()
        self.brush = QBrush()

        # Initialize with default values
        self.default()

        # Set pen and brush initially
        self.painter.setPen(self.pen)
        self.painter.setBrush(self.brush)

    def default(self) -> None:
        """Reset pen and brush to default values."""
        # Update pen properties directly
        self.pen.setColor(QColor(255, 255, 255, 255))
        self.pen.setWidth(1)
        self.pen.setStyle(Qt.PenStyle.SolidLine)
        self.pen.setCosmetic(True)  # Make pen cosmetic by default for pixel-perfect drawing

        # Update brush properties directly
        self.brush.setColor(QColor(255, 255, 255, 255))
        self.brush.setStyle(Qt.BrushStyle.SolidPattern)

    def save(self) -> None:
        """Save the current painter state."""
        self.painter.save()

    def restore(self) -> None:
        """Restore the painter state and reapply current pen and brush."""
        self.painter.restore()
        self.painter.setPen(self.pen)
        self.painter.setBrush(self.brush)

    def setPen(
        self    : 'PainterContext',
        color   : QColor,
        width   : float = 0,
        style   : Qt.PenStyle = Qt.PenStyle.SolidLine
    ) -> None:
        """Set the pen properties and apply to the painter.

        Args:
            color: The pen color
            width: The pen width (0 for cosmetic pen)
            style: The pen style (solid, dashed, etc.)
        """
        self.pen.setColor(color)
        self.pen.setWidth(width)
        self.pen.setStyle(style)
        self.painter.setPen(self.pen)

    def setBrush(
        self    : 'PainterContext',
        color   : QColor,
        style   : Qt.BrushStyle = Qt.BrushStyle.SolidPattern
    ) -> None:
        """Set the brush properties and apply to the painter.

        Args:
            color: The brush color
            style: The brush style (solid, pattern, etc.)
        """
        self.brush.setColor(color)
        self.brush.setStyle(style)
        self.painter.setBrush(self.brush)

    def setAll(
        self        : 'PainterContext',
        pen_color   : QColor,
        pen_width   : float = 1,
        pen_style   : Qt.PenStyle = Qt.PenStyle.SolidLine,
        brush_color : QColor | None = None,
        brush_style : Qt.BrushStyle = Qt.BrushStyle.SolidPattern
    ) -> None:
        self.setPen(pen_color, pen_width, pen_style)
        if brush_color is None:
            brush_color = pen_color
        self.setBrush(brush_color, brush_style)

    def noBrush(self : 'PainterContext') -> None:
        self.brush.setStyle(Qt.BrushStyle.NoBrush)
        self.painter.setBrush(self.brush)

    def setPenOnly(
        self    : 'PainterContext',
        color   : QColor,
        width   : float = 1,
        style   : Qt.PenStyle = Qt.PenStyle.SolidLine
    ) -> None:
        self.setPen(color, width, style)
        self.noBrush()

T = TypeVar('T')
class TypedList(Generic[T]):
    """A list that only accepts items of specific types.

    This class provides type safety by ensuring that only items of specified types
    can be added to the list. It's a generic class that can be parameterized with
    any type.

    Example:
        # Create a list that only accepts strings and integers
        typed_list = TypedList(str, int)
        typed_list.append("hello")  # OK
        typed_list.append(42)       # OK
        typed_list.append(3.14)     # TypeError
    """

    item_types: Tuple[Type[T], ...]
    items: List[T]

    def __init__(
        self   : 'TypedList[T]',
        *types : Type[T],
        items  : Optional[List[T]] = None
    ) -> None:
        """Initialize a TypedList with specified allowed types.

        Args:
            *types: Variable number of types that are allowed in this list
            items: Optional initial items to add to the list
        """
        self.item_types = types
        self.items: List[T] = []
        if items is not None:
            self.extend(items)

    def append(self, item: T) -> None:
        """Add an item to the list if it's of an allowed type.

        Args:
            item: The item to add

        Raises:
            TypeError: If the item is not of an allowed type
        """
        if not isinstance(item, self.item_types):
            allowed_types = ", ".join(t.__name__ for t in self.item_types)
            raise TypeError(f"Expected item of type {allowed_types}, got {type(item).__name__}")
        self.items.append(item)

    def extend(self, items: List[T]) -> None:
        """Add multiple items to the list if they're all of allowed types.

        Args:
            items: The items to add

        Raises:
            TypeError: If any item is not of an allowed type
        """
        for item in items:
            self.append(item)

    def __getitem__(self, index: int) -> T:
        """Get an item by index.

        Args:
            index: The index of the item to get

        Returns:
            The item at the specified index
        """
        return self.items[index]

    def __len__(self) -> int:
        """Get the number of items in the list.

        Returns:
            The number of items
        """
        return len(self.items)

    def __iter__(self) -> Iterator[T]:
        """Get an iterator over the items in the list.

        Returns:
            An iterator over the items
        """
        return iter(self.items)

class Library:
    name    : str
    symbols : TypedList['Symbol']

    def __init__(
        self    : 'Library',
        name    : str,
        symbols : TypedList['Symbol']
    ) -> None:
        self.name    = name
        self.symbols = symbols
