from types import SimpleNamespace
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QColor

from common import ORG_NAME, APP_NAME
from default.default_themes import DEFAULT_THEMES

class Themes:
    def __init__(self):
        self.themes = {}
        # attempt to load themes from settings
        settings = QSettings(ORG_NAME, APP_NAME)
        settings.beginGroup('themes')
        for themeName in settings.childGroups():
            self.themes[themeName] = SimpleNamespace()
            settings.beginGroup(themeName)
            self.loadTheme(self.themes[themeName], settings)
            settings.endGroup() # themeName
        # ensure that standard themes exist; add (and write to settings) if not
        for n, d in DEFAULT_THEMES.items():
            if n not in self.themes:
                self.themes[n] = SimpleNamespace()
                self.buildTheme(self.themes[n], d)
                settings.beginGroup(n)
                self.saveTheme(self.themes[n], settings)
                settings.endGroup() # n

    def get(self, name):
        return self.themes[name]

    # reset standard themes, do not touch user defined themes
    def reset(self):
        settings = QSettings(ORG_NAME, APP_NAME)
        settings.beginGroup('themes')
        for themeName, themeDict in DEFAULT_THEMES.items():
            themes[themeName] = SimpleNamespace()
            self.buildTheme(themeDict, themes[themeName])
            settings.beginGroup(themeName)
            self.saveTheme(themes[themeName], settings)
            settings.endGroup() # themeName

    def buildTheme(self, inst, themeDict):
        for k, v in themeDict.items():
            if isinstance(v, dict):
                setattr(inst, k, SimpleNamespace())
                self.buildTheme(getattr(inst, k), v)
            else:
                setattr(inst, k, v)

    def loadTheme(self, inst, settings):
        for n in settings.childKeys():
            setattr(inst, n, settings.value(n))
        for n in settings.childGroups():
            settings.beginGroup(n)
            setattr(inst, n, SimpleNamespace())
            self.loadTheme(getattr(inst, n), settings)
            settings.endGroup() # n

    def saveTheme(self, inst, settings):
        for k, v in inst.__dict__.items():
            if isinstance(v, SimpleNamespace):
                settings.beginGroup(k)
                self.saveTheme(v, settings)
                settings.endGroup() # k
            else:
                settings.setValue(k, v)

themes = Themes()
