from __future__ import annotations

import time

from typing import Self

from PyQt6.QtCore    import Qt, QRect, QRectF, QTimer
from PyQt6.QtWidgets import QSplashScreen, QApplication, QWidget
from PyQt6.QtGui     import QPixmap, QFont, QColor, QPainter

from ..app       import app
from ..resources import getIconPath

from ..core.defs import APP_NAME

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..widgets.window import Window


_splash : Splash | None = None


def progress(message : str, fraction : float) -> None:
    """Update the splash, if one is showing. Safe when it is not."""
    if _splash is not None:
        _splash.progress(message, fraction)


class Splash(QSplashScreen):
    _SIZE             = 0.25   # fraction of screen size
    _BITMAP_SIZE      = 0.1    # fraction of screen size
    _TEXT_SIZE        = 0.05   # fraction of screen size
    _GAP              = 0.025  # fraction of screen size
    _MIN_DISPLAY_TIME = 1500   # milliseconds
    _BAR_MARGIN       = 0.06   # fraction of splash width
    _BAR_HEIGHT       = 0.028  # fraction of splash height

    _start_time : float | None = None
    _message    : str = "Initialising..."
    _progress   : float = 0.0
    _light      : bool = True

    def __init__(self : Self, light : bool, parent=None):
        if (screen := QApplication.primaryScreen()) is None:
            raise RuntimeError("No screen")
        screen_geometry = screen.geometry()
        splash_width = int(screen_geometry.width() * self._SIZE)
        splash_height = int(screen_geometry.height() * self._SIZE)
        pixmap = self._create_splash_pixmap(
            splash_width, splash_height, screen_geometry.width(), light
        )
        super().__init__(pixmap)
        self._light = light
        self.setWindowFlags(
            Qt.WindowType.SplashScreen |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )
        self._start_time = None

    def _create_splash_pixmap(
        self          : Self,
        splash_width  : int,
        splash_height : int,
        screen_width  : int,
        light         : bool
    ) -> QPixmap:
        if (screen := QApplication.primaryScreen()) is None:
            raise RuntimeError("No screen")
        screen_geometry = screen.geometry()
        bitmap = QPixmap(getIconPath("ConnectEd.png"))
        pixmap = QPixmap(splash_width, splash_height)
        bg_color = Qt.GlobalColor.white if light else QColor("#202020")
        fg_color = Qt.GlobalColor.black if light else Qt.GlobalColor.lightGray
        pixmap.fill(bg_color)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gap = int(screen_width * self._GAP)
        bitmap_size = int(screen_geometry.height() * self._BITMAP_SIZE)
        text_size = int(screen_geometry.height() * self._TEXT_SIZE)
        font = QFont()
        font.setPixelSize(text_size)
        painter.setFont(font)
        text = APP_NAME
        text_metrics = painter.fontMetrics()
        text_width = text_metrics.horizontalAdvance(text)
        text_height = text_metrics.height()
        scaled_bitmap = bitmap.scaled(
            bitmap_size,
            bitmap_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        total_content_width = scaled_bitmap.width() + gap + text_width
        start_x = (splash_width - total_content_width) // 2
        bitmap_y = (splash_height - scaled_bitmap.height()) // 2
        painter.drawPixmap(start_x, bitmap_y, scaled_bitmap)
        painter.setPen(Qt.GlobalColor.black)
        surround = QRectF(start_x, bitmap_y, bitmap_size + 1, bitmap_size + 1)
        painter.drawRect(surround)
        text_x = start_x + scaled_bitmap.width() + gap
        text_y = (splash_height + text_height) // 2 - text_metrics.descent()
        painter.setPen(fg_color)
        painter.drawText(text_x, text_y, text)
        painter.end()
        return pixmap

    def show(self : Self):
        global _splash
        _splash = self
        super().show()
        self.raise_()
        self._start_time = time.time()
        self.progress(self._message, self._progress)

    def progress(self : Self, message : str, fraction : float) -> None:
        self._message = message
        self._progress = min(1.0, max(0.0, fraction))
        self.raise_()
        self.repaint()
        QApplication.processEvents()

    def drawContents(self : Self, painter : QPainter | None) -> None:
        if painter is None:
            return
        width = self.width()
        height = self.height()
        margin = max(16, int(width * self._BAR_MARGIN))
        bar_height = max(8, int(height * self._BAR_HEIGHT))
        bar = QRect(margin, height - margin - bar_height, width - 2 * margin, bar_height)
        track = QColor("#d0d0d0") if self._light else QColor("#404040")
        fill = QColor("#3d7ab5") if self._light else QColor("#6aa6e0")
        fg = Qt.GlobalColor.black if self._light else Qt.GlobalColor.lightGray
        painter.fillRect(bar, track)
        done = bar.adjusted(0, 0, int(bar.width() * self._progress) - bar.width(), 0)
        if done.width() > 0:
            painter.fillRect(done, fill)
        font = QFont()
        font.setPixelSize(max(12, bar_height))
        painter.setFont(font)
        painter.setPen(fg)
        text = QRect(margin, bar.top() - bar_height * 2, bar.width(), bar_height * 2)
        painter.drawText(
            text,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self._message,
        )

    def finish(self : Self, w : QWidget | None):
        from .window import Window
        if not isinstance(w, Window):
            raise TypeError("Bad widget")
        if self._start_time is not None:
            elapsed = (time.time() - self._start_time) * 1000
            if elapsed < self._MIN_DISPLAY_TIME:
                remaining_time = int(self._MIN_DISPLAY_TIME - elapsed)
                QTimer.singleShot(remaining_time, lambda: self._actually_finish(w))
                return
        self._actually_finish(w)

    def _actually_finish(self : Self, window : Window):
        global _splash
        _splash = None
        super().finish(window)
        window.show()
        window.raise_()
        window.activateWindow()
        window.statusBar().status.setText("Ready")
        app().ready.splash.emit()
