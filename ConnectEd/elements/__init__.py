__all__ = [
    'LineSpec',
    'FillSpec',
    'PainterContext',
    'Element',
    'Rectangle',
]

from dataclasses import dataclass
from typing      import Optional
from types       import SimpleNamespace

from PyQt6.QtCore    import Qt
from PyQt6.QtGui     import QPainter, QPen, QBrush, QColor
from PyQt6.QtWidgets import QWidget


@dataclass
class LineSpec:
    color : Optional[QColor]      = None
    width : Optional[float]       = None
    style : Optional[Qt.PenStyle] = None

@dataclass
class FillSpec:
    color : Optional[QColor]        = None
    style : Optional[Qt.BrushStyle] = None

class Element:
    pass

class PainterContext:
    """A context object that bundles painter with a reusable pen and brush."""

    painter : QPainter
    pen     : QPen
    brush   : QBrush

    def __init__(self, widget: QWidget) -> None:
        """Initialize a PainterContext with a widget to paint on.

        Args:
            widget: The QWidget to paint on
        """
        self.painter = QPainter(widget)
        self.pen = QPen()
        self.pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        self.pen.setCapStyle(Qt.PenCapStyle.RoundCap)
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
        brush_color : Optional[QColor] = None,
        brush_style : Qt.BrushStyle = Qt.BrushStyle.SolidPattern
    ) -> None:
        self.setPen(pen_color, pen_width, pen_style)
        if brush_color is None:
            brush_color = pen_color
        self.setBrush(brush_color, brush_style)

    def setAlpha(self : 'PainterContext', alpha : int) -> None:
        self.pen.color().setAlpha(alpha)
        self.brush.color().setAlpha(alpha)

    def noPen(self : 'PainterContext') -> None:
        self.pen.setStyle(Qt.PenStyle.NoPen)
        self.painter.setPen(self.pen)

    def noBrush(self : 'PainterContext') -> None:
        self.brush.setStyle(Qt.BrushStyle.NoBrush)
        self.painter.setBrush(self.brush)

    def setPenOnly(
        self    : 'PainterContext',
        color   : QColor,
        width   : float = 0,
        style   : Qt.PenStyle = Qt.PenStyle.SolidLine
    ) -> None:
        self.setPen(color, width, style)
        self.noBrush()

    def setBrushOnly(
        self    : 'PainterContext',
        color   : QColor,
        style   : Qt.BrushStyle = Qt.BrushStyle.SolidPattern
    ) -> None:
        self.setBrush(color, style)
        self.noPen()

    def setFromAttrs(
        self : 'PainterContext',
        element : 'Element',
        prefs   : SimpleNamespace,
        theme   : SimpleNamespace
    ) -> None:
        if hasattr(element, 'line'):
            self.setPen(
                element.line.color if element.line.color else theme.line,
                element.line.width if element.line.width else prefs.line.width,
                element.line.style if element.line.style else prefs.line.style
            )
        else:
            self.noPen()
        if hasattr(element, 'fill'):
            self.setBrush(
                element.fill.color if element.fill.color else theme.fill,
                element.fill.style if element.fill.style else prefs.fill
            )
        else:
            self.noBrush()

from .rectangle import Rectangle
