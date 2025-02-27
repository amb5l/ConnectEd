from typing import Type, List, Tuple, Generic, TypeVar, Union

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

    def __init__(self, widget : QWidget) -> None:
        self.painter = QPainter(widget)
        self.pen = QPen()
        self.brush = QBrush()

        # Initialize with default values
        self.default()

        # Set pen and brush initially
        self.painter.setPen(self.pen)
        self.painter.setBrush(self.brush)

    def default(self) -> None:
        # Update pen properties directly
        self.pen.setColor(QColor(255, 255, 255, 255))
        self.pen.setWidth(1)
        self.pen.setStyle(Qt.PenStyle.SolidLine)
        self.pen.setCosmetic(True)  # Make pen cosmetic by default for pixel-perfect drawing

        # Update brush properties directly
        self.brush.setColor(QColor(255, 255, 255, 255))
        self.brush.setStyle(Qt.BrushStyle.SolidPattern)

    def save(self) -> None:
        self.painter.save()

    def restore(self) -> None:
        self.painter.restore()
        self.painter.setPen(self.pen)
        self.painter.setBrush(self.brush)

    def setPen(
        self    : 'PainterContext',
        color   : QColor,
        width   : float = 0,
        style   : Qt.PenStyle = Qt.PenStyle.SolidLine
    ) -> None:
        self.pen.setColor(color)
        self.pen.setWidth(width)
        self.pen.setStyle(style)
        self.painter.setPen(self.pen)

    def setBrush(
        self    : 'PainterContext',
        color   : QColor,
        style   : Qt.BrushStyle = Qt.BrushStyle.SolidPattern
    ) -> None:
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
    item_types : Tuple[Type[T], ...]
    items      : List[T]

    def __init__(
        self   : 'TypedList',
        *types : Type[T],
        items  : Union[None, List[T]] = None
    ):
        self.item_types = types
        self.items: List[T] = []
        if items is not None:
            self.append(items)

    def append(self, item: T):
        if not isinstance(item, self.item_types):
            allowed_types = ", ".join(t.__name__ for t in self.item_types)
            raise TypeError(f"Expected item of type {allowed_types}, got {type(item).__name__}")
        self.items.append(item)

    def extend(self, items: List[T]):
        for item in items:
            self.append(item)

    def __getitem__(self, index: int) -> T:
        return self.items[index]

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self):
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
