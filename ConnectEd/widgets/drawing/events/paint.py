from PyQt6.QtCore import Qt, QRect, QRectF, QSize, QSizeF, QPoint, QPointF
from PyQt6.QtGui  import QPaintEvent, QResizeEvent, QPainter, QPen, QBrush, QColor

from ....core import settings, PainterContext, _iround

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

    def paintEvent(self: 'Drawing', event: QPaintEvent) -> None:
        """Handle paint events for the Drawing widget.

        This method is called whenever the widget needs to be redrawn.
        It paints the background, elements, grid, and selection rectangle.

        Args:
            event: The paint event
        """
        ctx = PainterContext(self)
        ctx.painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # fill background
        ctx.setBrush(settings.theme.background, settings.prefs.display.background)
        ctx.painter.fillRect(self.view_rect.physical, ctx.brush)

        # transition to logical coordinates
        ctx.save()
        ctx.painter.scale(self.zoom, self.zoom)
        ctx.painter.translate(QPointF(0.5, 0.5) - self.pan)

        # draw sheet (if applicable)
        self.paintSheet(ctx)

        # draw diagram contents
        for element in self.elements:
            element.paint(ctx)
        for element in self.wip:
            element.paint(ctx)

        # draw grid if enabled
        if self.grid.display:
            self._paintGrid(ctx)

        # transition back to physical coordinates
        ctx.restore()

        # draw selection rectangle if active
        if self.sel_rect:
            ctx.save()
            ctx.painter.setCompositionMode(QPainter.CompositionMode.RasterOp_SourceXorDestination)
            ctx.setPen(QColor(255, 255, 255), width=1, style=Qt.PenStyle.DotLine)
            ctx.noBrush()
            ctx.painter.drawRect(self.sel_rect.physical)
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

    def _viewUpdate(self : 'Drawing') -> None:
        self.view_rect.setPhysical(self.visibleRegion().boundingRect())
        self.main_window.status_bar.zoom.setText('{:.2f}%'.format(self.zoom * 100))
        self.update()
