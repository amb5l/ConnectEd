import os, platform
from types import SimpleNamespace
from PyQt6.QtCore import Qt, QSettings, QSizeF
from PyQt6.QtGui import QColor

from common import ORG_NAME, APP_NAME
from .themes import themes
from default.default_prefs import DEFAULT_PREFS


class PrefsMngr:
    def __init__(self):
        self.prefs = SimpleNamespace()
        # attempt to load preferences from settings, otherwise use defaults
        settings = QSettings(ORG_NAME, APP_NAME)
        settings.beginGroup('prefs')
        self.loadPrefs(self.prefs, settings)
        # check existence of required preferences, set to default if missing
        self.checkPrefs(self.prefs, DEFAULT_PREFS, settings)
        # replace theme name with theme instance
        #print('self.prefs.draw.theme:', self.prefs.draw.theme, type(self.prefs.draw.theme))
        self.prefs.draw.theme = themes.get(self.prefs.draw.theme)
        # default paths
        if platform.system() == 'Windows':
            if 'WORK' in os.environ:
                defaultPath = os.environ['WORK']
            elif 'USERPROFILE' in os.environ:
                defaultPath = os.environ['USERPROFILE']
            elif 'HOMEPATH' in os.environ:
                defaultPath = os.environ['HOMEPATH']
            elif 'HOMEDRIVE' in os.environ:
                defaultPath = os.environ['HOMEDRIVE']
            else:
                defaultPath = 'C:'
        else:
            if 'WORK' in os.environ:
                defaultPath = os.environ['WORK']
            else:
                defaultPath = '~'
        if self.prefs.file.open.dir is None:
            self.prefs.file.open.dir = defaultPath
        if self.prefs.file.save.dir is None:
            self.prefs.file.save.dir = defaultPath

    def loadPrefs(self, inst, settings):
        for n in settings.childKeys():
            #print('loading prefs value:', settings.group() + '/' + n)
            setattr(inst, n, self.fromSetting(settings.value(n)))
        for n in settings.childGroups():
            setattr(inst, n, SimpleNamespace())
            settings.beginGroup(n)
            self.loadPrefs(getattr(inst, n), settings)
            settings.endGroup() # n

    def checkPrefs(self, inst, prefsDict, settings):
        for k, v in prefsDict.items():
            if not hasattr(inst, k):
                if isinstance(v, dict):
                    #print('missing prefs category:', k)
                    setattr(inst, k, SimpleNamespace())
                    settings.beginGroup(k)
                    self.checkPrefs(getattr(inst, k), v, settings)
                    settings.endGroup()
                else:
                    #print('missing prefs value, applying default:', k)
                    setattr(inst, k, v)
                    #print('writing persistant setting:', settings.group() + '/' + k)
                    settings.setValue(k, self.toSetting(v))

    def toSetting(self, x):
        typeName = type(x).__name__
        match typeName:
            case 'NoneType'           : valueStr = 'None'; valueStr = ''
            case 'str'                : valueStr = x
            case 'int'                : valueStr = str(x)
            case 'float'              : valueStr = str(x)
            case 'bool'               : valueStr = str(x)
            case 'QSizeF'             : valueStr = f'({x.width()},{x.height()})'
            case 'PyQt6.QtGui.QColor' : typeName = 'QColor'; valueStr = str(x)
            case 'PenStyle'           : valueStr = str(x).replace('PenStyle.', '')
            case 'BrushStyle'         : valueStr = str(x).replace('BrushStyle.', '')
            case _ :
                raise ValueError(f'Prefs.toSetting: unsupported type = {typeName}')
        #print(f'toSetting: {typeName}:{valueStr}')
        return typeName + ':' + valueStr

    def fromSetting(self, s):
        typeName, valueStr = s.split(':', 1)
        #print(f'fromSetting: {typeName}:{valueStr}')
        r = None
        match typeName:
            case 'None'       : r = None
            case 'str'        : r = valueStr
            case 'int'        : r = int   (valueStr)
            case 'float'      : r = float (valueStr)
            case 'bool'       : r = valueStr == 'True'
            case 'QSizeF'     : r = QSizeF(*map(float, valueStr[1:-1].split(',')))
            case 'QColor'     : r = QColor(valueStr)
            case 'PenStyle'   : r = Qt.PenStyle[valueStr]
            case 'BrushStyle' : r = Qt.BrushStyle[valueStr]
        if r is not None:
            return r
        raise ValueError(f'Prefs.fromSetting: unsupported type = {typeName}')

prefsMngr = PrefsMngr()
prefs = prefsMngr.prefs
