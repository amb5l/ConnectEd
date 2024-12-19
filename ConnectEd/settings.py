# TODO support XML export/import of settings

from types import SimpleNamespace
from PyQt6.QtCore import Qt, QSettings, QSizeF
from PyQt6.QtGui import QColor

from common import logger, ORG_NAME, APP_NAME
from defaults import DEFAULT_PREFS, DEFAULT_THEMES, FACTORY_SHEET_SIZES


class Settings:
    def __init__(self):
        self.startup = {}
        self.prefs = SimpleNamespace()
        self.themes = SimpleNamespace()
        self.theme = SimpleNamespace()
        self.sheet_sizes = {}

    def reset(self):
        logger.debug('clearing all settings')
        qsettings = QSettings(ORG_NAME, APP_NAME)
        qsettings.clear()

    def load(self):
        qsettings = QSettings(ORG_NAME, APP_NAME)
        # startup
        logger.debug('loading settings: startup')
        self.startup.clear()
        qsettings.beginGroup('startup')
        for k in qsettings.childKeys():
            self.startup[k] = self.convTextToQSetting(qsettings.value(k))
        qsettings.endGroup()
        # preferences
        logger.debug('loading settings: preferences')
        qsettings.beginGroup('prefs')
        self.loadNamespace(qsettings, self.prefs)
        self.defaultMissingSettings(qsettings, self.prefs, DEFAULT_PREFS)
        qsettings.endGroup()
        # themes
        logger.debug('loading settings: themes')
        qsettings.beginGroup('themes')
        self.loadNamespace(qsettings, self.themes)
        self.defaultMissingSettings(qsettings, self.themes, DEFAULT_THEMES)
        qsettings.endGroup()
        # sheet sizes
        logger.debug('loading settings: sheet sizes')
        self.sheet_sizes.clear()
        self.sheet_sizes.update(FACTORY_SHEET_SIZES)
        qsettings.beginGroup('sheet_sizes')
        for k in qsettings.childKeys():
            if k not in self.sheet_sizes:
                self.sheet_sizes[k] = self.convTextToQSetting(qsettings.value(k))
        qsettings.endGroup()
        # theme
        self.theme = getattr(self.themes, self.prefs.display.theme)

    def loadNamespace(self, qsettings, ns):
        for k in qsettings.childKeys():
            v = qsettings.value(k)
            logger.debug(f'loading setting: {qsettings.group() + "/" + k} = {v}')
            setattr(ns, k, self.convTextToQSetting(v))
        for g in qsettings.childGroups():
            setattr(ns, g, SimpleNamespace())
            qsettings.beginGroup(g)
            self.loadNamespace(qsettings, getattr(ns, g))
            qsettings.endGroup()

    def saveNamespace(self, qsettings, ns):
        for k, v in vars(ns).items():
            if isinstance(v, dict):
                qsettings.beginGroup(k)
                self.saveNamespace(v)
                qsettings.endGroup()
            else:
                qsettings.setValue(k, self.convQSettingToText(v))

    def save(self):
        logger.debug('saving settings')
        qsettings = QSettings(ORG_NAME, APP_NAME)
        # preferences
        qsettings.beginGroup('prefs')
        self.saveNamespace(qsettings, self.prefs)
        qsettings.endGroup()
        # themes
        qsettings.beginGroup('themes')
        self.saveNamespace(qsettings, self.themes)
        qsettings.endGroup()
        # sheet sizes
        qsettings.beginGroup('sheet_sizes')
        for k, v in self.sheet_sizes.items():
            qsettings.setValue(k, self.convQSettingToText(v))
        qsettings.endGroup()

    def defaultMissingSettings(self, qsettings, ns, defaults):
        for k, v in defaults.items():
            if not hasattr(ns, k):
                if isinstance(v, dict):
                    logger.debug(f'missing settings group, creating: {k}')
                    setattr(ns, k, SimpleNamespace())
                    qsettings.beginGroup(k)
                    self.defaultMissingSettings(qsettings, getattr(ns, k), defaults[k])
                    qsettings.endGroup()
                else:
                    logger.debug(f'missing settings value, applying default: {k} = {self.convQSettingToText(v)}')
                    setattr(ns, k, v)
                    qsettings.setValue(k, self.convQSettingToText(v))

    def convQSettingToText(self, x):
        typeName = type(x).__name__
        match typeName:
            case 'NoneType'   : valueStr = 'None'
            case 'str'        : valueStr = x
            case 'int'        : valueStr = str(x)
            case 'float'      : valueStr = str(x)
            case 'bool'       : valueStr = str(x)
            case 'QSizeF'     : valueStr = f'({x.width()},{x.height()})'
            case 'QColor'     : valueStr = hex(x.rgba())
            case 'PenStyle'   : valueStr = str(x).replace('PenStyle.', '')
            case 'BrushStyle' : valueStr = str(x).replace('BrushStyle.', '')
            case _ :
                raise ValueError(f'toQSettingValue: unsupported type = {typeName}')
        return typeName + ':' + valueStr

    def convTextToQSetting(self, s):
        typeName, valueStr = s.split(':', 1)
        r = None
        match typeName:
            case 'NoneType'   : r = None
            case 'str'        : r = valueStr
            case 'int'        : r = int   (valueStr)
            case 'float'      : r = float (valueStr)
            case 'bool'       : r = valueStr == 'True'
            case 'QSizeF'     : r = QSizeF(*map(float, valueStr[1:-1].split(',')))
            case 'QColor'     : r = QColor.fromRgba(int(valueStr,0))
            case 'PenStyle'   : r = Qt.PenStyle[valueStr]
            case 'BrushStyle' : r = Qt.BrushStyle[valueStr]
            case _:
                raise ValueError(f'fromQSettingValue: unsupported type = {typeName}')
        return r

    def dump(self, x, indent = '  '):
        if isinstance(x, SimpleNamespace):
            for k, v in vars(x).items():
                if isinstance(v, SimpleNamespace):
                    print(f'{indent}{k}:')
                    self.dump(v, indent + '  ')
                else:
                    print(f'{indent}{k} = {self.convQSettingToText(v)}')
        elif isinstance(x, dict):
            for k, v in x.items():
                if isinstance(v, dict):
                    self.dump(v, indent + '  ')
                else:
                    print(f'{indent}{k} = {self.convQSettingToText(v)}')

settings = Settings()
startup = settings.startup
prefs = settings.prefs
themes = settings.themes
theme = settings.theme
sheet_sizes = settings.sheet_sizes