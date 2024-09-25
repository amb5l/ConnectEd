from types import SimpleNamespace
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QColor

from app import ORG_NAME, APP_NAME


#-------------------------------------------------------------------------------
# standard themes with default colors are defined here

DEFAULT_THEMES = {
    "dark": {
        "background"    : QColor(  8,    8,   8 ),
        "sheet"         : QColor(  16,  16,  16 ),
        "edge"          : QColor( 255,   0,   0 ),
        "grid"          : QColor(  32,  32,  32 ),
        "border"        : QColor(  64,  64,  64 ),
        "titleBlock"    : QColor(  64,  64,  64 ),
        "selected" : {
            "line"      : QColor( 255,   0, 255 ),
            "fill"      : QColor(  32,   0,  32 )
        },
        "highlighted" : {
            "line"      : QColor( 255, 255,   0 ),
            "fill"      : QColor(  32,  32,   0 )
        },
        "moving"      : {
            "line"      : QColor( 255, 255, 255 ),
            "fill"      : None
        },
        "block"       : {
            "line"      : QColor(   0, 128, 128 ),
            "fill"      : QColor(   0, 128, 128 ),
            "property"  : QColor( 128, 128,   0 )
        }
    },
    "light": {
        "background"    : QColor( 128, 128, 128 ),
        "sheet"         : QColor( 255, 255, 255 ),
        "grid"          : QColor( 192, 192, 192 ),
        "border"        : QColor(  64,  64,  64 ),
        "titleBlock"    : QColor(  64,  64,  64 ),
        "selected" : {
            "line"      : QColor( 255,   0, 255 ),
            "fill"      : QColor( 192, 192, 192 )
        },
        "highlighted" : {
            "line"      : QColor( 255, 255,   0 ),
            "fill"      : QColor( 192, 192, 192 )
        },
        "moving"      : {
            "line"      : QColor( 255, 255, 255 ),
            "fill"      : None
        },
        "block"       : {
            "line"      : QColor(   0, 128, 128 ),
            "fill"      : QColor(   0, 128, 128 ),
            "property"  : QColor( 128, 128,   0 )
        }
    },
    "print": {
        "background"    : QColor( 128, 128, 128 ),
        "sheet"         : QColor( 255, 255, 255 ),
        "grid"          : QColor( 192, 192, 192 ),
        "border"        : QColor(  64,  64,  64 ),
        "titleBlock"    : QColor(  64,  64,  64 ),
        "selected" : {
            "line"      : QColor( 255,   0, 255 ),
            "fill"      : QColor( 192, 192, 192 )
        },
        "highlighted" : {
            "line"      : QColor( 255, 255,   0 ),
            "fill"      : QColor( 192, 192, 192 )
        },
        "moving"      : {
            "line"      : QColor( 255, 255, 255 ),
            "fill"      : None
        },
        "block"       : {
            "line"      : QColor(   0, 128, 128 ),
            "fill"      : QColor(   0, 128, 128 ),
            "property"  : QColor( 128, 128,   0 )
        }
    }
}

class Themes:
    def __init__(self):
        self.themes = {}
        # attempt to load themes from settings
        settings = QSettings(ORG_NAME, APP_NAME)
        settings.beginGroup("themes")
        for themeName in settings.childGroups():
            self.themes[themeName] = SimpleNamespace()
            settings.beginGroup(themeName)
            self._loadTheme(self.themes[themeName], settings)
            settings.endGroup() # themeName
        # ensure that standard themes exist; add (and write to settings) if not
        for n, d in DEFAULT_THEMES.items():
            if n not in self.themes:
                self.themes[n] = SimpleNamespace()
                self._buildTheme(self.themes[n], d)
                settings.beginGroup(n)
                self._saveTheme(self.themes[n], settings)
                settings.endGroup() # n

    def get(self, name):
        return self.themes[name]

    # reset standard themes, do not touch user defined themes
    def reset(self):
        settings = QSettings(ORG_NAME, APP_NAME)
        settings.beginGroup("themes")
        for themeName, themeDict in DEFAULT_THEMES.items():
            themes[themeName] = SimpleNamespace()
            self._buildTheme(themeDict, themes[themeName])
            settings.beginGroup(themeName)
            self._saveTheme(themes[themeName], settings)
            settings.endGroup() # themeName

    def _buildTheme(self, inst, themeDict):
        for k, v in themeDict.items():
            if isinstance(v, dict):
                setattr(inst, k, SimpleNamespace())
                self._buildTheme(getattr(inst, k), v)
            else:
                setattr(inst, k, v)

    def _loadTheme(self, inst, settings):
        for n in settings.childKeys():
            setattr(inst, n, settings.value(n))
        for n in settings.childGroups():
            settings.beginGroup(n)
            setattr(inst, n, SimpleNamespace())
            self._loadTheme(getattr(inst, n), settings)
            settings.endGroup() # n

    def _saveTheme(self, inst, settings):
        for k, v in inst.__dict__.items():
            if isinstance(v, SimpleNamespace):
                settings.beginGroup(k)
                self._saveTheme(v, settings)
                settings.endGroup() # k
            else:
                settings.setValue(k, v)

#-------------------------------------------------------------------------------
# single instance (TODO: consider... per canvas? per window?)

themes = Themes()

#-------------------------------------------------------------------------------
