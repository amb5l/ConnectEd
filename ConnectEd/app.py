from PyQt6.QtGui import QColor, QColorConstants, QFont

#-------------------------------------------------------------------------------

ORGNAME = "ConnectEd"
APPNAME = "PyConnectEd"
APPTITLE = "ConnectEd"

#-------------------------------------------------------------------------------

# TODO save/restore many of these in settings

#-------------------------------------------------------------------------------

class Colors:
    def __init__(
        self,
        background,
        grid,
        blockOutline,
        blockFill,
        blockProperty
    ):
        self.background    = background
        self.grid          = grid
        self.blockOutline  = blockOutline
        self.blockFill     = blockFill
        self.blockProperty = blockProperty

factoryDark = Colors(
    QColor(24,24,24),                  # background
    QColor(100,100,100),               # grid
    QColor(0,0,128),                  # blockOutline
    QColor(0,0,32),                  # blockFill
    QColorConstants.Svg.aqua           # blockProperty
)

#-------------------------------------------------------------------------------

def Font(font, size, bold=False, italic=False, underline=False):
    r = QFont(font, size)
    r.setBold(bold)
    r.setItalic(italic)
    r.setUnderline(underline)
    return r

class Fonts:
    default       = QFont()
    blockProperty = QFont()

    def __init__(
        self,
        default,
        blockProperty
    ):
        self.default       = default
        self.blockProperty = blockProperty

defaultFonts = Fonts(
    default       = Font("Arial", 7),
    blockProperty = Font("Courier", 7)
)

#-------------------------------------------------------------------------------

class Grid:
    def __init__(self, x, y):
        self.x = x
        self.y = y

defaultGrid = Grid(10, 10)

#-------------------------------------------------------------------------------

class Preferences:
    def __init__(self, colors, fonts, grid):
        self.colors = colors
        self.fonts  = fonts
        self.grid   = grid

preferences = Preferences(
    colors = factoryDark,
    fonts  = defaultFonts,
    grid   = defaultGrid
)
