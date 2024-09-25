from types import SimpleNamespace
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QColor

from common import ORG_NAME, APP_NAME
from themes import themes
from .prefs_default import PREFS_DEFAULT


class Prefs:
    def __init__(self):
        self.prefs = SimpleNamespace()
        # attempt to load preferences from settings, otherwise use defaults
        settings = QSettings(ORG_NAME, APP_NAME)
        settings.beginGroup("prefs")
        self.loadPrefs(self.prefs, settings)
        # check existence of required preferences, set to default if missing
        self.checkPrefs(self.prefs, PREFS_DEFAULT, settings)
        # replace theme name with theme object
        print("self.prefs.draw.theme:", self.prefs.draw.theme, type(self.prefs.draw.theme))
        self.prefs.draw.theme = themes.get(self.prefs.draw.theme)

    def __call__(self):
        return self.prefs

    def loadPrefs(self, inst, settings):
        for n in settings.childKeys():
            print("loading prefs value:", settings.group() + "/" + n)
            setattr(inst, n, self._fromSetting(settings.value(n)))
        for n in settings.childGroups():
            setattr(inst, n, SimpleNamespace())
            settings.beginGroup(n)
            self.loadPrefs(getattr(inst, n), settings)
            settings.endGroup() # n

    def checkPrefs(self, inst, prefsDict, settings):
        for k, v in prefsDict.items():
            if not hasattr(inst, k):
                if isinstance(v, dict):
                    print("missing prefs category:", k)
                    setattr(inst, k, SimpleNamespace())
                    settings.beginGroup(k)
                    self.checkPrefs(getattr(inst, k), v, settings)
                    settings.endGroup()
                else:
                    print("missing prefs value, applying default:", k)
                    setattr(inst, k, v)
                    print("writing persistant setting:", settings.group() + "/" + k)
                    settings.setValue(k, self.toSetting(v))

    def toSetting(self, x):
        typeName = type(x).__name__
        match typeName:
            case "str"                : pass
            case "int"                : pass
            case "float"              : pass
            case "bool"               : pass
            case "tuple"              : pass
            case "PyQt6.QtGui.QColor" : typeName = "QColor"
            case "PenStyle"           : pass
            case "BrushStyle"         : pass
            case _ :
                raise ValueError(f"Prefs.toSetting: unsupported type = {typeName}")
        return typeName + ":" + str(x)

    def _fromSetting(self, s):
        typeName, valueStr = s.split(":", 1)
        match typeName:
            case "str"        : return valueStr
            case "int"        : return int   (valueStr)
            case "float"      : return float (valueStr)
            case "bool"       : return valueStr == "True"
            case "tuple"      : return tuple (map(float, valueStr.split(",")))
            case "QColor"     : return QColor(valueStr)
            case "PenStyle"   : return Qt.PenStyle(int(valueStr))
            case "BrushStyle" : return Qt.BrushStyle(int(valueStr))
        raise ValueError(f"Prefs.fromSetting: unsupported type = {typeName}")

prefs = Prefs()
