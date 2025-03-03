"""
Common types and utility classes for the ConnectEd application.

This module provides reusable type definitions and utility classes
used throughout the application, including painting contexts and typed collections.
"""

__all__ = [
    'TypedList',
    'Library',
    'PainterContext'
]

from typing import Type, List, Tuple, Generic, TypeVar, Optional, Iterator

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui     import QPainter, QPen, QBrush, QColor

from typing import TYPE_CHECKING
if TYPE_CHECKING: # avoid circular import issues
    from ..widgets import Symbol


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
