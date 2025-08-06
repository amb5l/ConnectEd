import time

from typing import Optional, Self

from PyQt6.QtCore    import Qt, QRectF, QTimer
from PyQt6.QtWidgets import QSplashScreen, QApplication
from PyQt6.QtGui     import QPixmap, QFont, QColor, QPainter

from ..core.defs import APP_NAME

from .. import hub


class Splash(QSplashScreen):
    _SIZE             = 0.25   # fraction of screen size
    _BITMAP_SIZE      = 0.1    # fraction of screen size
    _TEXT_SIZE        = 0.05   # fraction of screen size
    _GAP              = 0.025  # fraction of screen size
    _MIN_DISPLAY_TIME = 1500   # milliseconds

    _start_time : Optional[float] = None

    def __init__(self : Self, light : bool, parent=None):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        splash_width = int(screen_geometry.width() * self._SIZE)
        splash_height = int(screen_geometry.height() * self._SIZE)
        pixmap = self._create_splash_pixmap(
            splash_width, splash_height, screen_geometry.width(), light
        )
        super().__init__(pixmap)
        self.setWindowFlags(
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
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        bitmap = QPixmap(f"{hub.APP_ROOT}/resources/icons/ConnectEd.png")
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

    def show(self):
        super().show()
        self._start_time = time.time()

    def finish(self, main_window):
        if self._start_time is not None:
            elapsed = (time.time() - self._start_time) * 1000
            if elapsed < self._MIN_DISPLAY_TIME:
                remaining_time = int(self._MIN_DISPLAY_TIME - elapsed)
                QTimer.singleShot(remaining_time, lambda: self._actually_finish(main_window))
                return
        self._actually_finish(main_window)

    def _actually_finish(self, main_window):
        super().finish(main_window)
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()
