from typing import Self

from PyQt6.QtGui import QPen

from ..... import hub


class OutlinePen:
    pen : QPen

    def __init__(self : Self) -> None:
        self.pen = QPen()
        self.onSettingsChange()

    def onSettingsChange(self : Self) -> None:
        self.pen.setColor(hub.settings.getTheme("selected/line"))
        self.pen.setWidthF(hub.settings.get("display/select/outline/width"))
        self.pen.setStyle(hub.settings.get("display/select/outline/style"))


class ElementOutlineMixin:
    outline : OutlinePen

    def initOutline(self : Self):
        self.outline = OutlinePen()
