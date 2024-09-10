from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

ORGNAME = "ConnectEd"
APPNAME = "PyConnectEd"
APPTITLE = "ConnectEd"

def Font(font, size, bold=False, italic=False, underline=False):
    r = QFont(font, size)
    r.setBold(bold)
    r.setItalic(italic)
    r.setUnderline(underline)
    return r

class MaxMin:
    def __init__(self, max, min):
        self.max = max
        self.min = min

class Prefs:
    class Dwg:
        zoom            = MaxMin(16.0, 0.1)
        panStep         = 0.125

        class Color:
            def __init__(self, background, highlight, select):
                self.background = background
                self.highlight  = highlight
                self.select     = select

        class Border:
            def __init__(self, enable, lineWidth, lineColor):
                self.enable    = enable
                self.lineWidth = lineWidth
                self.lineColor = lineColor

        class Grid:
            def __init__(self, x, y, enable, lineWidth, lineColor):
                self.enable    = enable
                self.lineWidth = lineWidth
                self.lineColor = lineColor

        class Block:
            class Debug:
                propertyOutline = False

            defaultDebug = Debug()

            def __init__(
                self,
                lineWidth,
                lineColor,
                fillColor,
                propertyFont,
                propertyColor,
                propertyOutline
            ):
                self.lineWidth       = lineWidth
                self.lineColor       = lineColor
                self.fillColor       = fillColor
                self.propertyFont    = propertyFont
                self.propertyColor   = propertyColor
                self.propertyOutline = propertyOutline

        def __init__(
            self,
            color,
            border,
            grid,
            block
        ):
            self.color  = color
            self.border = border
            self.grid   = grid
            self.block  = block

    class Edit:
        class Grid:
            def __init__(self, enable, x, y):
                self.enable = enable
                self.x      = x
                self.y      = y

        class Select:
            def __init__(self, enclose):
                self.enclose = enclose

        def __init__(self, grid, select):
            self.grid   = grid
            self.select = select

    class Kbd:
        escape = [Qt.Key.Key_Escape, False, False, False]
        def __init__(
            self,
            zoomIn,
            zoomOut,
            zoomFull,
            panLeft,
            panRight,
            panUp,
            panDown,
            addBlock
        ):
            self.zoomIn   = zoomIn
            self.zoomOut  = zoomOut
            self.zoomFull = zoomFull
            self.panLeft  = panLeft
            self.panRight = panRight
            self.panUp    = panUp
            self.panDown  = panDown
            self.addBlock = addBlock

    def __init__(self, dwg, edit, kbd):
        self.dwg  = dwg
        self.edit = edit
        self.kbd  = kbd

prefs = Prefs(
    dwg = Prefs.Dwg(
        color =     Prefs.Dwg.Color(
                        background = QColor(24,24,24),
                        highlight  = QColor(255,255,255),
                        select     = QColor(255,0,255)
                    ),
        border =    Prefs.Dwg.Border(
                        enable = True,
                        lineWidth = 0,
                        lineColor = QColor(0,255,0)
                    ),
        grid  =     Prefs.Dwg.Grid(
                        True,
                        10, 10,
                        0.0,
                        QColor(100,100,100)
                    ),
        block =     Prefs.Dwg.Block(
                        lineWidth       = 0,
                        lineColor       = QColor(0,0,224),
                        fillColor       = QColor(0,0,32),
                        propertyFont    = Font("Courier", 6),
                        propertyColor   = QColor(224,224,224),
                        propertyOutline = False
                    )
    ),
    edit = Prefs.Edit(
        grid   = Prefs.Edit.Grid(True, 10, 10),
        select = Prefs.Edit.Select(True)
    ),
    kbd = Prefs.Kbd(
        zoomIn   = [Qt.Key.Key_I,      False, False, False],
        zoomOut  = [Qt.Key.Key_O,      False, False, False],
        zoomFull = [Qt.Key.Key_F,      False, False, False],
        panLeft  = [Qt.Key.Key_Left,   False, False, False],
        panRight = [Qt.Key.Key_Right,  False, False, False],
        panUp    = [Qt.Key.Key_Up,     False, False, False],
        panDown  = [Qt.Key.Key_Down,   False, False, False],
        addBlock = [Qt.Key.Key_Insert, False, False, False]
    )
)
