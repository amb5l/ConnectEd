from PyQt6.QtCore import Qt, QRect, QRectF, QSize, QSizeF, QPoint, QPointF
from PyQt6.QtGui  import QPaintEvent, QResizeEvent, QPainter, QPen, QBrush, QColor

from ....core import settings, PainterContext
from ....core.utils import _iround

from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING: # avoid circular import issues
    from .. import Drawing


class DrawingEventsPaintMixin:
    def paintEvent(self : 'Drawing', event : QPaintEvent):
        ctx = PainterContext(self)
        ctx.painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        p = QRectF(self.visibleRegion().boundingRect()) # physical view rect
        l = QRectF(                                    # logical view rect
            self._p2l(p.topLeft()),
            self._p2l(p.bottomRight())
            )

        ctx.setBrush(settings.theme.background, settings.prefs.display.background)
        ctx.painter.fillRect(p, ctx.brush)

        ctx.save()
        ctx.painter.scale(self.zoom, self.zoom)
        ctx.painter.translate(QPointF(0.5, 0.5) - self.pan)
        for element in self.elements:
            element.paint(ctx)
        for element in self.wip:
            element.paint(ctx)
        if self.grid.display:
            self._paintGrid(ctx, l)
        ctx.restore()

        if self.sel_prect:
            ctx.save()
            ctx.painter.setCompositionMode(QPainter.CompositionMode.RasterOp_SourceXorDestination)
            ctx.setPen(QColor(255, 255, 255), width=1, style=Qt.PenStyle.DotLine)
            ctx.noBrush()
            ctx.painter.drawRect(self.sel_crect)
            ctx.restore()



    def _paintGrid(
        self  : 'Drawing',
        ctx   : PainterContext,
        lrect : QRectF
    ) -> None:
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

