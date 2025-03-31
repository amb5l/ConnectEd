"""
Settings management for the ConnectEd application.

This module provides classes for managing application settings,
including loading, saving, and accessing configuration values.
"""

# TODO:
# persistant settings for application
# session settings for diagram and library

__all__ = ['Settings']

from types       import SimpleNamespace
from typing      import Any, Dict, List, Union
from collections import namedtuple

from PyQt6.QtCore import QSettings, QPointF, QSizeF, Qt
from PyQt6.QtGui  import QColor

from .log import logger
from .defs   import ORG_NAME, APP_NAME
from .utils  import getDefaultPath


MinMax = namedtuple('MinMax', ['min', 'max'])

FACTORY_SETTINGS = {
    'startup': {
        'geometry': None
    },
    'prefs': {
        'file': {
            'new': {
                'sheet'  : 'A4',
                'margin' : 10
            },
            'open': {
                'dir': getDefaultPath()
            },
            'save': {
                'dir': getDefaultPath()
            }
        },
        'display': {
            'theme': 'dark',
            'overscan': {  # TODO set all to 0
                'top'    : 2,
                'bottom' : 2,
                'left'   : 2,
                'right'  : 2
            },
            'elements': {
                'extents': {
                    'line': {
                        'width': 0,
                        'style': Qt.PenStyle.SolidLine
                    },
                    'fill': Qt.BrushStyle.NoBrush,
                },
                'paper': {
                    'line': {
                        'width': 0,
                        'style': Qt.PenStyle.NoPen
                    },
                    'fill': Qt.BrushStyle.SolidPattern,
                },
                'border': {
                    'line': {
                        'width' : 1,
                        'style' : Qt.PenStyle.SolidLine
                    }
                },
                'rectangle': {
                    'line': {
                        'width': 1,
                        'style': Qt.PenStyle.SolidLine
                    },
                    'fill': Qt.BrushStyle.SolidPattern
                },
                'selected': {
                    'line': {
                        'width': 1,
                        'style': Qt.PenStyle.DotLine
                    },
                    'fill': Qt.BrushStyle.DiagCrossPattern,
                    'grip': {
                        'size': 4
                    }
                },
                'wip': {
                    'line': {
                        'width': 0,
                        'style': Qt.PenStyle.DashLine
                    },
                    'fill': Qt.BrushStyle.NoBrush
                },
                'alpha': 192
            },
            'zoom': {
                'padding' : 0.1,
                'step'  : 0.25,
                'limit' : MinMax(0.01, 100.0)
            },
            'pan': {
                'step' : 0.1
            },
        },
        'mouse': {
            'drag'  : 5,
            'wheel' : 120
        }
    },
    'themes': {
        'dark': {
            'vacuum': {
                'fill' : QColor(  16,  16,  16 )
            },
            'extents': {
                'line' : QColor(   0,   0, 255 ),
                'fill' : QColor(   0,   0,   0 )
            },
            'paper': {
                'fill' : QColor(  32,  32,  32 )
            },
            'border': {
                'line' : QColor( 128, 128, 128 )
            },
            'rectangle': {
                'line' : QColor( 192, 120,   0 ), # light orange
                'fill' : QColor(  96, 100,   0 )  # dark orange
            },
            'wip': {
                'line' : QColor(   0, 255,   0 ), # bright green
                'fill' : QColor(   0, 128,   0 )  # medium green
            },
            'selected': {
                'line' : QColor( 255,   0, 255 ), # bright magenta
                'fill' : QColor( 255,   0, 255 )  # bright magenta
            },
            'grip': {
                'line' : QColor( 255,   0, 255 ), # bright magenta
                'fill' : QColor( 255,   0,   0 )  # bright red

            },
            'anchor': {
                'line' : QColor( 255,   0, 255 ), # bright magenta
                'fill' : QColor( 255, 255, 128 )  # bright yellow
            },
            'grid': {
                'line' : QColor(  64,  64,  64 )
            }
        },
        'light': {
            'extents': {
                'line' : QColor(   0,   0, 255 ),
                'fill' : QColor(  16,  16,  16 )
            },
            'paper': {
                'fill' : QColor( 240, 240, 240 )
            },
            'border': {
                'line' : QColor( 128, 128, 128 )
            },
            'rectangle': {
                'line' : QColor( 192, 120,   0 ), # light orange
                'fill' : QColor(  96, 100,   0 )  # dark orange
            },
            'wip': {
                'line' : QColor(   0, 255,   0 ), # bright green
                'fill' : QColor(   0, 128,   0 )  # medium green
            },
            'selected': {
                'line' : QColor( 255,   0, 255 ), # bright magenta
                'fill' : QColor( 128,   0, 128 )  # medium magenta
            },
            'grip': {
                'line' : QColor( 255,   0, 255 ), # bright magenta
                'fill' : QColor( 255, 255, 128 )  # bright yellow
            },
            'grid': {
                'line' : QColor(  64,  64,  64 )
            }
        }
    },
    'sheet_sizes': {
        'A4' : QSizeF( 1169.0 ,  827.0 ),
        'A3' : QSizeF( 1654.0 , 1169.0 ),
        'A2' : QSizeF( 2338.0 , 1654.0 ),
        'A1' : QSizeF( 3307.0 , 2338.0 ),
        'A0' : QSizeF( 4677.0 , 3307.0 ),
        'A'  : QSizeF(  970.0 ,  720.0 ),
        'B'  : QSizeF( 1520.0 ,  970.0 ),
        'C'  : QSizeF( 2020.0 , 1520.0 ),
        'D'  : QSizeF( 3220.0 , 2020.0 ),
        'E'  : QSizeF( 4220.0 , 3220.0 )
    },
    'defaults': { # TODO move these to session settings
        'sheet'  : 'A4',
        'margin' : 10,
        'grid': {
            'display'    : True,
            'snap'       : True,
            'pitch'      : QPointF(10.0, 10.0),
            'dots'       : False,
            'alpha'      : 128,
            'min_pixels' : 10
        }
    }
}

class Settings(SimpleNamespace):
    @property
    def theme(self) -> SimpleNamespace:
        return getattr(self.themes, self.prefs.display.theme)

    def __init__(self : 'Settings') -> None:
        self._init(self, FACTORY_SETTINGS)

    def reset(self : 'Settings') -> None:
        logger.debug('clearing all saved settings')
        qsettings = QSettings(ORG_NAME, APP_NAME)
        qsettings.clear()

    def load(self : 'Settings') -> None:
        """Load settings from QSettings storage into this SimpleNamespace."""
        logger.debug('loading settings')
        qsettings = QSettings(ORG_NAME, APP_NAME)
        for attr_name in FACTORY_SETTINGS.keys():
            attr = getattr(self, attr_name)
            logger.debug(f'Loading settings for {attr_name}')
            qsettings.beginGroup(attr_name)
            self._load(attr, qsettings)
            qsettings.endGroup()

    def save(self : 'Settings') -> None:
        """Save settings from this SimpleNamespace to QSettings storage."""
        logger.debug('saving settings')
        qsettings = QSettings(ORG_NAME, APP_NAME)
        for attr_name in FACTORY_SETTINGS.keys():
            attr = getattr(self, attr_name)
            logger.debug(f'Saving settings for {attr_name}')
            qsettings.beginGroup(attr_name)
            self._save(attr, qsettings)
            qsettings.endGroup()

    def dump(self : 'Settings') -> str:
        """Return a formatted string representation of all settings."""
        lines: List[str] = []
        self._dump('settings', self, lines)
        return "\n".join(lines)

    def _init(
        self     : 'Settings',
        ns       : SimpleNamespace,
        settings : Union[Dict[str, Any], Any]
    ) -> None:
        """Initialize a SimpleNamespace with values from a dictionary."""
        if isinstance(settings, dict):
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
        """Recursively load settings from QSettings into a SimpleNamespace."""
        for group in qsettings.childGroups():
            setattr(ns, group, SimpleNamespace())
            qsettings.beginGroup(group)
            self._load(getattr(ns, group), qsettings)
            qsettings.endGroup()
        for key in qsettings.childKeys():
            value = qsettings.value(key)
            if value is not None:
                logger.debug(f'loading setting: {qsettings.group()}/{key} = {value}')
                try:
                    setattr(ns, key, self._text2value(value))
                except (ValueError, AttributeError) as e:
                    logger.warning(f'Error loading setting {key}: {e}')

    def _save(
        self      : 'Settings',
        ns        : SimpleNamespace,
        qsettings : QSettings
    ) -> None:
        """Recursively save settings from a SimpleNamespace to QSettings."""
        for key, value in vars(ns).items():
            if not key.startswith('_') and not callable(value):
                if isinstance(value, SimpleNamespace):
                    qsettings.beginGroup(key)
                    logger.debug(f'saving settings group: {qsettings.group()}')
                    self._save(value, qsettings)
                    qsettings.endGroup()
                else:
                    logger.debug(f'saving setting: {qsettings.group()}/{key} = {value}')
                    qsettings.setValue(key, self._value2text(value))

    def _text2value(self : 'Settings', text_value : str) -> Any:
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
            case 'MinMax'     : return MinMax(*map(float, valueStr[1:-1].split(',')))
            case 'QPointF'    : return QPointF(*map(float, valueStr[1:-1].split(',')))
            case 'QSizeF'     : return QSizeF(*map(float, valueStr[1:-1].split(',')))
            case 'QColor'     : return QColor.fromRgba(int(valueStr,0))
            case 'PenStyle'   : return Qt.PenStyle[valueStr]
            case 'BrushStyle' : return Qt.BrushStyle[valueStr]
            case _:
                raise ValueError(f'Unsupported type: {typeName}')

    def _value2text(self : 'Settings', value : Any) -> str:
        """Convert a Python value to a text representation for QSettings."""
        typeName = type(value).__name__
        match typeName:
            case 'NoneType'   : valueStr = 'None'
            case 'bytes'      : valueStr = value.hex()
            case 'str'        : valueStr = value
            case 'int'        : valueStr = str(value)
            case 'float'      : valueStr = str(value)
            case 'bool'       : valueStr = str(value)
            case 'MinMax'     : valueStr = f'({value.min},{value.max})'
            case 'QPointF'    : valueStr = f'({value.x()},{value.y()})'
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
                    lines.append(f'{indent}{name}/{k} = {self._value2text(v)}')
        else:
            lines.append(f'{indent}{name} = {self._value2text(x)}')

settings = Settings()
