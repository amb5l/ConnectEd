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
        'Restore'
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
        """Paint the grid on the drawing.

        Args:
            ctx: The painter context
            lrect: The logical rectangle to draw the grid in
        """
        if settings.prefs.display.grid.display:
            ctx.painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            g = settings.prefs.display.grid
            grect = QRectF(
                self.view_rect.logical.topLeft() - QPointF(g.x, g.y),
                self.view_rect.logical.bottomRight() + QPointF(g.x, g.y)
            ).toRect()
            ctx.setPenOnly(settings.theme.grid)
            ctx.setAlpha(settings.prefs.display.grid.alpha)
            if g.dots:
                for x in range(_iround(grect.left(), g.x), 1 + _iround(grect.right(), g.x), g.x):
                    for y in range(_iround(grect.top(), g.y), 1 + _iround(grect.bottom(), g.y), g.y):
                        ctx.painter.drawPoint(QPoint(x, y))
            else:
                for x in range(_iround(grect.left(), g.x), 1 +_iround(grect.right(), g.x), g.x):
                    ctx.painter.drawLine(
                        QPointF(x, grect.top()),
                        QPointF(x, grect.bottom())
                    )
                for y in range(_iround(grect.top(), g.y), 1 + _iround(grect.bottom(), g.y), g.y):
                    ctx.painter.drawLine(
                        QPointF(grect.left(), y),
                        QPointF(grect.right(), y)
                    )


