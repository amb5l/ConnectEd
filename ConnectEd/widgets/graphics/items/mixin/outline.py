from typing import Self

from PyQt6.QtGui import QPen

from .....app import settings


class OutlinePen:
    pen : QPen

    def __init__(self : Self) -> None:
        self.pen = QPen()
        self.onSettingsChange()

    def onSettingsChange(self : Self) -> None:
        self.pen.setColor(settings().get("theme/selected/line"))
        self.pen.setWidthF(settings().get("display/select/outline/width"))
        self.pen.setStyle(settings().get("display/select/outline/style"))


class ItemOutlineMixin:
    outline : OutlinePen

    def initOutline(self : Self):
        self.outline = OutlinePen()
