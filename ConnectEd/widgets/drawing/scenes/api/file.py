__all__ = ["DrawingApiFileMixin"]

from PyQt6.QtCore import QFile, QIODevice, QXmlStreamWriter, QXmlStreamReader

from .....core import toXmlBegin, toXmlEnd

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import Drawing


class DrawingApiFileMixin:
    def save(self : "Drawing", path: str) -> None:
        # TODO error handling
        file = QFile(path)
        if file.open(
            QIODevice.OpenModeFlag.WriteOnly | QIODevice.OpenModeFlag.Text
        ):
            xw = QXmlStreamWriter(file)
            toXmlBegin(xw)
            self.toXml(xw)
            toXmlEnd(xw)
            file.close()

    @classmethod
    def load(cls, path: str) -> "Drawing":
        # TODO error handling
        file = QFile(path)
        if file.open(
            QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text
        ):
            xr = QXmlStreamReader(file)
            instance = cls.fromXml(xr)
            file.close()
            return instance
