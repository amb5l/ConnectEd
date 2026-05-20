from typing import Self

from PyQt6.QtCore    import Qt, QSize, QRectF
from PyQt6.QtWidgets import QApplication, QStyle
from PyQt6.QtGui     import QColor, QPainter, QPixmap, \
                            QIcon, QFont, QFontMetrics
from PyQt6.QtSvg     import QSvgRenderer

from ..app import logger, settings

from .check import checked


@checked
def getDefaultIconSize() -> int:
    app = QApplication.instance()
    style = app.style()
    return style.pixelMetric(QStyle.PixelMetric.PM_SmallIconSize)


@checked
def getFgBgColors() -> tuple[QColor, QColor]:
    if settings().get("display/theme") == "dark":
        return QColor(Qt.GlobalColor.white), QColor(Qt.GlobalColor.black)
    else:
        return QColor(Qt.GlobalColor.black), QColor(Qt.GlobalColor.white)


@checked
def getSvgIcon(path : str, size : QSize, margin : int = 0) -> QIcon:
    fg_color, _ = getFgBgColors()
    pixmap = QPixmap(size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    with open(path) as f:
        svg_content = f.read()
    svg_content = svg_content.replace('currentColor', QColor(fg_color).name())
    renderer = QSvgRenderer(svg_content.encode('utf-8'))
    if not renderer.isValid():
        logger().error("Invalid SVG file")
        return QIcon()
    svg_size = renderer.defaultSize()
    scale_factor = min(
        (size.width()  - (2 * margin)) / svg_size.width(),
        (size.height() - (2 * margin)) / svg_size.height()
    )
    scaled_size = svg_size * scale_factor
    x = ( size.width()  - scaled_size.width()  ) / 2
    y = ( size.height() - scaled_size.height() ) / 2
    painter.translate(x, y)
    renderer.render(
        painter,
        QRectF(0, 0, scaled_size.width(), scaled_size.height())
    )
    painter.end()
    # TODO: invert colors for dark theme?
    return QIcon(pixmap)


class SvgIconSingleton:
    PATH : str
    SIZE : QSize

    _instance = None
    _icon     = None

    def __new__(cls : type[Self]) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self : Self) -> None:
        pass

    @checked
    def get(self : Self) -> QIcon:
        if self._icon is None:
            self._icon = getSvgIcon(self.PATH, self.SIZE)
        return self._icon


@checked
def getCharIcon(
    family : str,
    char   : str,
    size   : QSize,
    margin : int = 1
) -> QIcon:
    char = char[0] if char else " "
    fg_color, bg_color = getFgBgColors()
    pixmap = QPixmap(size)
    pixmap.fill(bg_color)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    font = QFont(family)
    w = size.width()  - (2 * margin)
    h = size.height() - (2 * margin)
    font_size = min(w, h)
    font.setPixelSize(font_size)
    metrics = QFontMetrics(font)
    while font_size > 1:
        bounding_rect = metrics.tightBoundingRect(char)
        if bounding_rect.width() <= w and bounding_rect.height() <= h:
            break
        font_size -= 1
        font.setPixelSize(font_size)
        metrics = QFontMetrics(font)
    painter.setFont(font)
    painter.setPen(fg_color)
    text_rect = QRectF(margin, margin, w, h)
    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, char)
    painter.end()
    return QIcon(pixmap)


class CharIconSingleton:
    FONT_FAMILY : str
    CHAR        : str
    SIZE        : QSize
    MARGIN      : int

    _instance = None
    _icon     = None

    MARGIN = 1

    def __new__(cls : type[Self]) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self : Self) -> None:
        pass

    @checked
    def get(self : Self) -> QIcon:
        if self._icon is None:
            self._icon = getCharIcon(
                self.FONT_FAMILY, self.CHAR, self.SIZE, self.MARGIN
            )
        return self._icon
