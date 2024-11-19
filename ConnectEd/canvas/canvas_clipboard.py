# use QSvgGenerator
# remember DPI with resolution

from PyQt6.QtCore import QSize, QRect, QBuffer, QIODevice
from PyQt6.QtSvg import QSvgGenerator

from common import APP_NAME, MIME_TYPE

buf = QBuffer()
buf.open(QIODevice.OpenModeFlag.WriteOnly)
generator = QSvgGenerator
generator.setOutputDevice(buf)
generator.setTitle(APP_NAME)
# write buf to clipboard
# empty buf
buf.buffer().clear()

class CanvasClipboardMixin:
    def cut(self):
        # copy selected items to clipboard then remove them from diagram
        # produce an SVG version of the clipboard content
        # produce a bitmap version of the clipboard content
        pass
    def copy(self):
        # copy selected items to clipboard
        # produce an SVG version of the clipboard content
        # produce a bitmap version of the clipboard content
        pass
    def paste(self):
        pass

    def clipboardHasData(self):
        return self.clipboard.mimeData().hasFormat(MIME_TYPE)