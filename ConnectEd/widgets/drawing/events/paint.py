from math import ceil

from PyQt6.QtCore import Qt, QRect, QRectF, QSize, QSizeF, QPoint, QPointF
from PyQt6.QtGui  import QPaintEvent, QResizeEvent, QPainter, QPen, QBrush, QColor

from ....core     import settings, _iround
from ....elements import PainterContext

from typing import TYPE_CHECKING
if TYPE_CHECKING: # avoid circular import issues
    from .. import Drawing


class DrawingEventsPaintMixin:
    """Mixin class that handles paint events for Drawing widgets.

    This class provides methods for painting the drawing contents, including:
    - Background
    - Elements
    - Grid
    - Selection rectangle
    """
    PAINT_SEQUENCE = [
        'Background',
        'Save',
        'GoLogical',
        'Elements',
        'WIP',
        'Grid',
        'Restore',
        'SelectRect'
    ]

    def paintEvent(self: 'Drawing', event: QPaintEvent) -> None:
        """Handle paint events for the Drawing widget.

        This method is called whenever the widget needs to be redrawn.
        It paints the background, elements, grid, etc.

        Args:
            event: The paint event
        """
        ctx = PainterContext(self)
        ctx.painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        for step in self.PAINT_SEQUENCE:
            fn = getattr(self, f'_paint{step}')
            fn(ctx)

    def _paintBackground(self: 'Drawing', ctx: PainterContext) -> None:
        ctx.setBrush(settings.theme.background, settings.prefs.display.background)
        ctx.painter.fillRect(self.view_rect.physical, ctx.brush)

    def _paintSave(self: 'Drawing', ctx: PainterContext) -> None:
        ctx.save()

    def _paintGoLogical(self: 'Drawing', ctx: PainterContext) -> None:
        ctx.painter.scale(self.zoom, self.zoom)
        ctx.painter.translate(QPointF(0.5, 0.5) - self.pan)

    def _paintElements(self: 'Drawing', ctx: PainterContext) -> None:
        for element in self.elements:
            element.paint(ctx)

    def _paintWIP(self: 'Drawing', ctx: PainterContext) -> None:
        for element in self.wip:
            element.paint(ctx)

    def _paintRestore(self: 'Drawing', ctx: PainterContext) -> None:
        ctx.restore()

    def _paintGrid(self: 'Drawing', ctx: PainterContext) -> None:
        def align(x : float, px : float) -> float:
            return px * int(x / px)
        g = settings.prefs.display.grid
        if g.show:
            ctx.painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            px = g.pitch.x()
            if px * self.zoom < g.pixels.min:
                px *= ceil(g.pixels.min / (g.pitch.x() * self.zoom))
            py = g.pitch.y()
            if py * self.zoom < g.pixels.min:
                py *= ceil(g.pixels.min / (g.pitch.y() * self.zoom))
            grect = QRectF(
                self.view_rect.logical.topLeft() - QPointF(px, py),
                self.view_rect.logical.bottomRight() + QPointF(px, py)
            ).toRect()
            ctx.setPenOnly(settings.theme.grid)
            ctx.setAlpha(settings.prefs.display.grid.alpha)
            if g.dots:
                x = align(grect.left(), px)
                while x <= grect.right():
                    y = align(grect.top(), py)
                    while y <= grect.bottom():
                        ctx.painter.drawPoint(QPoint(x, y))
                        y += py
                    x += px
            else:
                x = align(grect.left(), px)
                while x <= grect.right():
                    ctx.painter.drawLine(
                        QPointF(x, grect.top()),
                        QPointF(x, grect.bottom())
                    )
                    x += px
                y = align(grect.top(), py)
                while y <= grect.bottom():
                    ctx.painter.drawLine(
                        QPointF(grect.left(), y),
                        QPointF(grect.right(), y)
                    )
                    y += py

    def _paintSelectRect(self: 'Drawing', ctx: PainterContext) -> None:
        if self.sel_rect:
            ctx.save()
            ctx.painter.setCompositionMode(QPainter.CompositionMode.RasterOp_SourceXorDestination)
            ctx.painter.setPen(QPen(QColor(255, 255, 255), 1, Qt.PenStyle.DotLine))
            ctx.painter.setBrush(Qt.BrushStyle.NoBrush)
            ctx.painter.drawRect(self.sel_rect.physical)
            ctx.restore()
