from PyQt6.QtGui import QColor, QColorConstants, QFont

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
        zoom    = MaxMin(16.0, 0.1)
        panStep = 0.125
        background = QColor()

        class Grid:
            def __init__(self, x, y, lineWidth, lineColor):
                self.x         = x
                self.y         = y
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

        def __init__(self, background, grid, block):
            self.background = background
            self.grid       = grid
            self.block      = block

    def __init__(self, dwg):
        self.dwg = dwg

prefs = Prefs(
    # drawing preferences
    dwg = Prefs.Dwg(
        background = QColor(24,24,24),
        grid       = Prefs.Dwg.Grid(10, 10, 0.0, QColor(100,100,100)),
        block      = Prefs.Dwg.Block(
                        lineWidth       = 0,
                        lineColor       = QColor(0,0,224),
                        fillColor       = QColor(0,0,32),
                        propertyFont    = Font("Courier", 7),
                        propertyColor   = QColor(224,224,224),
                        propertyOutline = False
                    )
    )
)
