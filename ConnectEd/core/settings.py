from types import SimpleNamespace

from PyQt6.QtCore import QSettings, QSize, QSizeF, Qt
from PyQt6.QtGui  import QColor

from .logger import logger
from .defs   import ORG_NAME, APP_NAME
from .types  import FontSpec


class Settings:
    startup : SimpleNamespace

    def __init__(self):
        self.startup = SimpleNamespace()

    def reset(self):
        logger.debug('clearing all settings')
        qsettings = QSettings(ORG_NAME, APP_NAME)
        qsettings.clear()

    def load(self):
        qsettings = QSettings(ORG_NAME, APP_NAME)
        logger.debug('loading settings: startup')
        qsettings.beginGroup('startup')
        self._loadNamespace(qsettings, self.startup)
        qsettings.endGroup()

    def save(self):
        logger.debug('saving settings')
        qsettings = QSettings(ORG_NAME, APP_NAME)
        qsettings.beginGroup('startup')
        self._saveNamespace(qsettings, self.startup)
        qsettings.endGroup()

    def _loadNamespace(self, qsettings, ns):
        for k in qsettings.childKeys():
            v = qsettings.value(k)
            logger.debug(f'loading setting: {qsettings.group() + "/" + k} = {v}')
            setattr(ns, k, self._TextToQSetting(v))
        for g in qsettings.childGroups():
            setattr(ns, g, SimpleNamespace())
            qsettings.beginGroup(g)
            self._loadNamespace(qsettings, getattr(ns, g))
            qsettings.endGroup()

    def _saveNamespace(self, qsettings, ns):
        for k, v in vars(ns).items():
            if isinstance(v, SimpleNamespace):
                qsettings.beginGroup(k)
                self._saveNamespace(qsettings, v)
                qsettings.endGroup()
            elif isinstance(v, dict):
                qsettings.beginGroup(k)
                self._saveNamespace(qsettings, v)
                qsettings.endGroup()
            else:
                logger.debug(f'saving setting: {k} = {v}')
                qsettings.setValue(k, self._QSettingToText(v))

    def _TextToQSetting(self, s):
        typeName, valueStr = s.split(':', 1)
        r = None
        match typeName:
            case 'NoneType'      : r = None
            case 'bytes'         : r = bytes.fromhex(valueStr)
            case 'str'           : r = valueStr
            case 'int'           : r = int(valueStr)
            case 'float'         : r = float(valueStr)
            case 'bool'          : r = valueStr == 'True'
            case 'QSize'         : r = QSize(*map(int, valueStr[1:-1].split(',')))
            case 'QSizeF'        : r = QSizeF(*map(float, valueStr[1:-1].split(',')))
            case 'QColor'        : r = QColor.fromRgba(int(valueStr,0))
            case 'PenStyle'      : r = Qt.PenStyle[valueStr]
            case 'BrushStyle'    : r = Qt.BrushStyle[valueStr]#
            case 'FontSpec'      : r = FontSpec.__initFromStr__(valueStr)
            case 'AlignmentFlag' : r = Qt.AlignmentFlag(int(valueStr))
            case _:
                raise ValueError(f'fromQSettingValue: unsupported type = {typeName}')
        return r

    def _QSettingToText(self, x):
        typeName = type(x).__name__
        match typeName:
            case 'NoneType'      : valueStr = 'None'
            case 'bytes'         : valueStr = x.hex()
            case 'str'           : valueStr = x
            case 'int'           : valueStr = str(x)
            case 'float'         : valueStr = str(x)
            case 'bool'          : valueStr = str(x)
            case 'QSize'         : valueStr = f'({x.width()},{x.height()})'
            case 'QSizeF'        : valueStr = f'({x.width()},{x.height()})'
            case 'QColor'        : valueStr = hex(x.rgba())
            case 'PenStyle'      : valueStr = str(x).replace('PenStyle.', '')
            case 'BrushStyle'    : valueStr = str(x).replace('BrushStyle.', '')
            case 'FontSpec'      : valueStr = str(x)
            case 'AlignmentFlag' : valueStr = str(x)
            case _ :
                raise ValueError(f'toQSettingValue: unsupported type = {typeName}')
        return typeName + ':' + valueStr
