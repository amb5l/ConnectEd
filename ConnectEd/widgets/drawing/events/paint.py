from PyQt6.QtCore import Qt, QRect, QRectF, QSize, QSizeF, QPoint, QPointF
from PyQt6.QtGui  import QPaintEvent, QResizeEvent, QPainter, QPen, QBrush, QColor

from ....core import settings, PainterContext
from ....core.utils import _iround

from typing import TYPE_CHECKING, Optional, List, cast
if TYPE_CHECKING: # avoid circular import issues
    from .. import Drawing


class DrawingEventsPaintMixin:
    """Mixin class that handles paint events for Drawing widgets.

    This class provides methods for painting the drawing contents, including:
    - Background
    - Elements
    - Grid
    - Selection rectangle
    - Debug information
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

        # Get physical and logical view rectangles
        p = QRectF(self.visibleRegion().boundingRect())  # physical view rect
        l = QRectF(                                      # logical view rect
            self._p2l(p.topLeft()),
            self._p2l(p.bottomRight())
        )

        # Fill background
        ctx.setBrush(settings.theme.background, settings.prefs.display.background)
        ctx.painter.fillRect(p, ctx.brush)

        # Draw diagram contents
        ctx.save()
        ctx.painter.scale(self.zoom, self.zoom)
        ctx.painter.translate(QPointF(0.5, 0.5) - self.pan)

        # Draw elements
        for element in self.elements:
            element.paint(ctx)
        for element in self.wip:
            element.paint(ctx)

        # Draw grid if enabled
        if self.grid.display:
            self._paintGrid(ctx, l)

        ctx.restore()

        # Draw selection rectangle if active
        if self.sel_prect:
            ctx.save()
            ctx.painter.setCompositionMode(QPainter.CompositionMode.RasterOp_SourceXorDestination)
            ctx.setPen(QColor(255, 255, 255), width=1, style=Qt.PenStyle.DotLine)
            ctx.noBrush()
            ctx.painter.drawRect(self.sel_crect)
            ctx.restore()

    def _paintGrid(
        self: 'Drawing',
        ctx: PainterContext,
        lrect: QRectF
    ) -> None:
        """Paint the grid on the drawing.

        Args:
            ctx: The painter context
            lrect: The logical rectangle to draw the grid in
        """
        if settings.prefs.display.grid.display:
            ctx.save()
            ctx.painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            g = settings.prefs.display.grid
            grect = QRectF(
                lrect.topLeft() - QPointF(g.x, g.y),
                lrect.bottomRight() + QPointF(g.x, g.y)
            ).toRect()
            ctx.setPenOnly(settings.theme.grid)
            if g.dots:
                for x in range(_iround(grect.left(), g.x), 1 + _iround(grect.right(), g.x), g.x):
                    for y in range(_iround(grect.top(), g.y), 1 + _iround(grect.bottom(), g.y), g.y):
                        ctx.painter.drawPoint(QPoint(x, y))
            else:
                for x in range(_iround(grect.left(), g.x), 1 +_iround(grect.right(), g.x), g.x):
                    ctx.painter.drawLine(
                        QPointF(x + 0.5, grect.top()),
                        QPointF(x + 0.5, grect.bottom())
                    )
                for y in range(_iround(grect.top(), g.y), 1 + _iround(grect.bottom(), g.y), g.y):
                    ctx.painter.drawLine(
                        QPointF(grect.left(), y + 0.5),
                        QPointF(grect.right(), y + 0.5)
                    )
            ctx.restore()

    def _viewUpdate(self : 'Drawing'):
        self.update()

