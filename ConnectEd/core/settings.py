from types import SimpleNamespace
from typing import Any
from PyQt6.QtCore import QSettings, QSize, QSizeF, Qt
from PyQt6.QtGui  import QColor

from .logger import logger
from .defs   import ORG_NAME, APP_NAME
from .utils  import get_default_path


FACTORY_SETTINGS = {
    'prefs': {
        'file': {
            'new': {
                'sheet'  : 'A4',
                'margin' : 10
            },
            'open': {
                'dir': get_default_path()
            },
            'save': {
                'dir': get_default_path()
            }
        },
        'display': {
            'theme': 'dark',
            'background': Qt.BrushStyle.SolidPattern,
            'grid': {
                'display' : True,
                'snap'    : True,
                'x'       : 10,
                'y'       : 10,
                'dots'    : False,
                'line': {
                    'width': 0,
                    'style': Qt.PenStyle.SolidLine
                }
            },
            'debug': {
                'overscan' : True,
                'canvas'   : True
            }
        }
    },
    'themes': {
        'dark': {
            'background': QColor(0, 0, 0, 255),
            'grid': QColor(32, 32, 32, 128)
        },
        'light': {
            'background': QColor(128, 128, 128, 255),
            'grid': QColor(32, 32, 32, 128)
        }
    }
}

class Settings(SimpleNamespace):
    @property
    def theme(self) -> SimpleNamespace:
        return getattr(self.themes, self.prefs.display.theme)

    def __init__(self : 'Settings'):
        self._init(self, FACTORY_SETTINGS)

    def reset(self : 'Settings'):
        logger.debug('clearing all saved settings')
        qsettings = QSettings(ORG_NAME, APP_NAME)
        qsettings.clear()

    def load(self : 'Settings'):
        """Load settings from QSettings storage into this SimpleNamespace."""
        logger.debug('loading settings')
        qsettings = QSettings(ORG_NAME, APP_NAME)
        for attr_name in dir(self):
            if attr_name.startswith('_') or callable(getattr(self, attr_name)):
                continue
            attr = getattr(self, attr_name)
            if hasattr(attr, '__fields__'): # is a Pydantic model
                logger.debug(f'Loading settings for {attr_name}')
                qsettings.beginGroup(attr_name)
                self._load(attr, qsettings)
                qsettings.endGroup()

    def save(self : 'Settings'):
        """Save settings from this SimpleNamespace to QSettings storage."""
        logger.debug('saving settings')
        qsettings = QSettings(ORG_NAME, APP_NAME)
        for attr_name in dir(self):
            if attr_name.startswith('_') or callable(getattr(self, attr_name)):
                continue
            attr = getattr(self, attr_name)
            if hasattr(attr, '__fields__'): # is a Pydantic model
                logger.debug(f'Saving settings for {attr_name}')
                qsettings.beginGroup(attr_name)
                self._save(attr, qsettings)
                qsettings.endGroup()

    def dump(self : 'Settings') -> str:
        lines = []
        self._dump('settings', self, lines)
        return "\n".join(lines)

    def _init(
        self     : 'Settings',
        ns       : SimpleNamespace,
        settings : dict | Any
    ) -> None:
        for key, value in settings.items():
            if isinstance(value, dict):
                setattr(ns, key, SimpleNamespace())
                self._init(getattr(ns, key), value)
            else:
                setattr(ns, key, value)

    def _load(
        self      : 'Settings',
        ns        : SimpleNamespace,
        qsettings : QSettings
    ) -> None:
        for group in qsettings.childGroups():
            setattr(ns, group, SimpleNamespace())
            qsettings.beginGroup(group)
            self._load(getattr(ns, group.name), qsettings)
            qsettings.endGroup()
        for key in qsettings.childKeys():
            value = qsettings.value(key)
            if value is not None:
                logger.debug(f'loading setting: {qsettings.group()}/{key} = {value}')
                try:
                    setattr(ns, key, self._text_to_value(value))
                except (ValueError, AttributeError) as e:
                    logger.warning(f'Error loading setting {key}: {e}')

    def _save(
        self      : 'Settings',
        ns        : SimpleNamespace,
        qsettings : QSettings
    ) -> None:
        for key, value in ns.__dict__.items():
            if not key.startswith('_') and not callable(value):
                if isinstance(value, SimpleNamespace):
                    qsettings.beginGroup(key)
                    logger.debug(f'saving settings group: {qsettings.group()}')
                    self._save(qsettings, value)
                    qsettings.endGroup()
                else:
                    logger.debug(f'saving setting: {qsettings.group()}/{key} = {value}')
                    qsettings.setValue(key, self._value_to_text(value))

    def _text_to_value(self : 'Settings', text_value : str) -> Any:
        """Convert a text value from QSettings to the appropriate Python type."""
        if not isinstance(text_value, str):
            return text_value
        try:
            typeName, valueStr = text_value.split(':', 1)
        except ValueError:
            # If there's no type prefix, return as is
            return text_value
        match typeName:
            case 'NoneType'   : return None
            case 'bytes'      : return bytes.fromhex(valueStr)
            case 'str'        : return valueStr
            case 'int'        : return int(valueStr)
            case 'float'      : return float(valueStr)
            case 'bool'       : return valueStr == 'True'
            case 'QSize'      : return QSize(*map(int, valueStr[1:-1].split(',')))
            case 'QSizeF'     : return QSizeF(*map(float, valueStr[1:-1].split(',')))
            case 'QColor'     : return QColor.fromRgba(int(valueStr,0))
            case 'PenStyle'   : return Qt.PenStyle[valueStr]
            case 'BrushStyle' : return Qt.BrushStyle[valueStr]
            case _:
                raise ValueError(f'Unsupported type: {typeName}')

    def _value_to_text(self : 'Settings', value : Any) -> str:
        """Convert a Python value to a text representation for QSettings."""
        typeName = type(value).__name__
        match typeName:
            case 'NoneType'   : valueStr = 'None'
            case 'bytes'      : valueStr = value.hex()
            case 'str'        : valueStr = value
            case 'int'        : valueStr = str(value)
            case 'float'      : valueStr = str(value)
            case 'bool'       : valueStr = str(value)
            case 'QSize'      : valueStr = f'({value.width()},{value.height()})'
            case 'QSizeF'     : valueStr = f'({value.width()},{value.height()})'
            case 'QColor'     : valueStr = hex(value.rgba())
            case 'PenStyle'   : valueStr = str(value).replace('PenStyle.', '')
            case 'BrushStyle' : valueStr = str(value).replace('BrushStyle.', '')
            case _ :
                raise ValueError(f'Unsupported type: {typeName}')
        return typeName + ':' + valueStr

    def _dump(
        self   : 'Settings',
        name   : str,
        x      : Any,
        lines  : list[str],
        indent : str = '  '
    ) -> None:
        if isinstance(x, SimpleNamespace):
            for k, v in vars(x).items():
                if isinstance(v, SimpleNamespace):
                    lines.append(f'{indent}{name}/{k}:')
                    self._dump(name + '/' + k, v, lines, indent + '  ')
                else:
                    lines.append(f'{indent}{name}/{k} = {self._value_to_text(v)}')
        else:
            lines.append(f'{indent}{name} = {self._value_to_text(x)}')
