"""
Settings management for the ConnectEd application.

This module provides classes for managing application settings,
including loading, saving, and accessing configuration values.
"""

# TODO:
# persistant settings for application
# session settings for diagram and library

__all__ = ["Settings"]

from types  import SimpleNamespace
from typing import Self, Optional, Any, Dict, List

from PyQt6.QtCore import Qt, QObject, pyqtSignal, QSettings, QPointF, QSizeF
from PyQt6.QtGui  import QColor

from .log   import logger
from .defs  import ORG_NAME, APP_NAME
from .utils import getDefaultPath, val2str, str2val


FACTORY_SETTINGS = {
    "startup" : {
        "geometry" : b''
    },
    "display" : {
        "theme" : "dark",
        "outline" : {
            "width" : 0,
            "style" : Qt.PenStyle.DotLine
        },
        "key_point" : {
            "radius" : 5
        },
        "zoom" : {
            "padding" : 0.1,
            "step"    : 0.25,
            "min"     : 0.01,
            "max"     : 100.0
        },
        "pan" : {
            "step" : 0.1
        }
    },
    "defaults" : {
        "extents"    : QSizeF(100, 100),
        "paper_size" : "A4",
        "margin"     : 10,
        "border"     : 1,
        "grid" : {
            "display"    : True,
            "snap"       : True,
            "pitch"      : QPointF(10.0, 10.0),
            "dots"       : False,
            "alpha"      : 128,
            "min_pixels" : 10
        },
        "elements" : {
            "Block" : {
                "line" : {
                    "width" : 1,
                    "style" : Qt.PenStyle.SolidLine
                },
                "fill" : Qt.BrushStyle.SolidPattern
            },
            "BlockPin" : {
                "line" : {
                    "width" : 1,
                    "style" : Qt.PenStyle.SolidLine
                },
                "fill" : Qt.BrushStyle.SolidPattern,
            },
            "BlockPinName" : {
                "text" : {
                    "family"    : "Liberation Sans",
                    "size"      : 7,
                    "bold"      : False,
                    "italic"    : False,
                    "underline" : False
                }
            },
            "PropertyText" : {
                "text" : {
                    "family"    : "Liberation Sans",
                    "size"      : 7,
                    "bold"      : False,
                    "italic"    : False,
                    "underline" : False
                }
            },
            "Rectangle" : {
                "line" : {
                    "width" : 1,
                    "style" : Qt.PenStyle.SolidLine
                },
                "fill" : Qt.BrushStyle.SolidPattern
            },
            "TextBlock" : {
                "text" : {
                    "family"    : "Liberation Sans",
                    "size"      : 7,
                    "bold"      : False,
                    "italic"    : False,
                    "underline" : False
                }
            },
            "Text" : {
                "text" : {
                    "family"    : "Liberation Sans",
                    "size"      : 7,
                    "bold"      : False,
                    "italic"    : False,
                    "underline" : False
                }
            }
        }
    },
    "prefs" : {
        "file" : {
            "new" : {
                "sheet"  : "A4",
                "margin" : 10
            },
            "open" : {
                "dir" : getDefaultPath()
            },
            "save" : {
                "dir" : getDefaultPath()
            }
        },
        "mouse" : {
            "drag"  : 5,
            "wheel" : 120
        }
    },
    "themes" : {
        "dark" : {
            "background" : {
                "fill" : QColor(   0,   0,   0 )
            },
            "paper" : {
                "fill" : QColor(  32,  32,  32 )
            },
            "border" : {
                "line" : QColor( 128, 128, 128 )
            },
            "elements" : {
                "Block" : {
                    "line" : QColor( 0x81, 0xD1, 0xCD ),
                    "fill" : QColor( 0x30, 0x30, 0x30 )
                },
                "BlockPin" : {
                    "line" : QColor( 0x81, 0xD1, 0xCD ),
                    "fill" : QColor( 0x30, 0x30, 0x30 ),
                    "text" : QColor( 0x81, 0xD1, 0xCD )
                },
                "BlockPinName" : {
                    "text" : QColor( 0x81, 0xD1, 0xCD )
                },
                "PropertyText" : {
                    "text" : QColor( 128, 255, 128 )
                },
                "Rectangle" : {
                    "line" : QColor( 192, 120,   0 ), # light orange
                    "fill" : QColor(  96, 100,   0 )  # dark orange
                },
                "TextBlock" : {
                    "text" : QColor( 255, 255, 255 )
                },
                "Text" : {
                    "text" : QColor( 255, 255, 255 )
                }
            },
            "selected" : {
                "line" : QColor( 192,   0, 192 ), # bright magenta
                "fill" : QColor( 128,   0, 128 ), # bright magenta
                "text" : QColor( 224,   0, 224 )  # bright magenta
            },
            "key_point" : {
                "line" : QColor( 255,   0, 255 ), # bright magenta
                "fill" : QColor( 255,   0, 255 ), # bright magenta
            },
            "grid" : {
                "line" : QColor(  64,  64,  64 )
            }
        },
        "light" : {
            "background" : {
                "fill" : QColor(  16,  16,  16 )
            },
            "paper" : {
                "fill" : QColor( 240, 240, 240 )
            },
            "border" : {
                "line" : QColor( 128, 128, 128 )
            },
            "rectangle" : {
                "line" : QColor( 192, 120,   0 ), # light orange
                "fill" : QColor(  96, 100,   0 )  # dark orange
            },
            "selected" : {
                "line" : QColor( 255,   0, 255 ), # bright magenta
                "fill" : QColor( 128,   0, 128 )  # medium magenta
            },
            "key_point" : {
                "line" : QColor( 255,   0, 255 ), # bright magenta
                "fill" : QColor( 255,   0, 255 ), # bright magenta
            },
            "grid" : {
                "line" : QColor(  64,  64,  64 )
            }
        }
    },
    "paper_sizes" : {
        "A4" : QSizeF( 1169.0 ,  827.0 ),
        "A3" : QSizeF( 1654.0 , 1169.0 ),
        "A2" : QSizeF( 2338.0 , 1654.0 ),
        "A1" : QSizeF( 3307.0 , 2338.0 ),
        "A0" : QSizeF( 4677.0 , 3307.0 ),
        "A"  : QSizeF(  970.0 ,  720.0 ),
        "B"  : QSizeF( 1520.0 ,  970.0 ),
        "C"  : QSizeF( 2020.0 , 1520.0 ),
        "D"  : QSizeF( 3220.0 , 2020.0 ),
        "E"  : QSizeF( 4220.0 , 3220.0 )
    }
}

class Settings(QObject):
    _settings : dict[str, Any]

    change = pyqtSignal()

    def __init__(self : Self) -> None:
        super().__init__()
        self._settings = self._deepCopy(FACTORY_SETTINGS)

    def get(self : Self, path : str) -> Any:
        value = self._get(self._settings, path)
        return self._toNamespace(value) if isinstance(value, dict) else value

    def getTheme(self : Self, path : str) -> Any:
        theme_name = self.get("display/theme")
        if theme_name not in self._settings["themes"]:
            logger.warning(f"Unknown theme: {theme_name}")
            theme_name = "dark"
        return self.get(f"themes/{theme_name}/{path}")

    def set(self : Self, path : str, value : Any, emit : bool = True) -> None:
        tn = type(value).__name__
        tnx = self._getSettingTypeName(path) # type name expected
        if tn != tnx:
            logger.warning(
                f"Bad type for setting {path} - expected {tnx} but got {tn}"
            )
            return
        self._set(self._settings, path, value)
        if emit:
            self.change.emit()

    def reset(self : Self) -> None:
        """Clear all saved settings from QSettings."""
        logger.info("Clearing all persistent settings")
        qsettings = QSettings(ORG_NAME, APP_NAME)
        qsettings.clear()
        self._settings = self._deepCopy(FACTORY_SETTINGS)
        self.change.emit()

    def load(self : Self) -> None:
        """Load settings from QSettings into the settings store."""
        logger.debug("Loading settings")
        qsettings = QSettings(ORG_NAME, APP_NAME)
        for group in FACTORY_SETTINGS.keys():
            qsettings.beginGroup(group)
            self._load(self._settings[group], qsettings, group)
            qsettings.endGroup()
        self.change.emit()

    def save(self : Self) -> None:
        """Save settings to QSettings storage."""
        logger.debug("Saving settings")
        qsettings = QSettings(ORG_NAME, APP_NAME)
        for group, value in self._settings.items():
            qsettings.beginGroup(group)
            self._save(value, qsettings, group)
            qsettings.endGroup()

    def dump(self : Self) -> str:
        """Return a formatted string representation of all settings."""
        lines: List[str] = []
        self._dump("settings", self._settings, lines)
        return "\n".join(lines)

    def _deepCopy(self, d : Dict) -> Dict:
        """Create a deep copy of a settings dictionary."""
        result = {}
        for k, v in d.items():
            if isinstance(v, dict):
                result[k] = self._deepCopy(v)
            else:
                result[k] = v
        return result

    def _get(self : Self, d : Dict, path : str) -> Any:
        """Retrieve a nested value from a dictionary by path."""
        path_parts = path.strip("/").split("/")
        current = d
        for part in path_parts:
            if not isinstance(current, dict) or part not in current:
                raise KeyError(f"Invalid settings path: {'/'.join(path_parts)}")
            current = current[part]
        return current

    def _set(self : Self, d : Dict, path : str, value : Any) -> None:
        """Set a nested value in a dictionary by path."""
        path_parts = path.strip("/").split("/")
        current = d
        for part in path_parts[:-1]:
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
        current[path_parts[-1]] = value

    def _getSettingTypeName(self : Self, path : str) -> Optional[str]:
        """Determine the expected type of a setting based on FACTORY_SETTINGS."""
        value = self._get(FACTORY_SETTINGS, path)
        return None if isinstance(value, dict) else type(value).__name__

    def _load(
        self      : Self,
        settings  : Dict,
        qsettings : QSettings,
        path      : str
    ) -> None:
        """Recursively load settings from QSettings."""
        for group in qsettings.childGroups():
            settings[group] = {}
            qsettings.beginGroup(group)
            self._load(settings[group], qsettings, f"{path}/{group}")
            qsettings.endGroup()
        for key in qsettings.childKeys():
            value = qsettings.value(key)
            if value is not None:
                full_path = f"{path}/{key}"
                type_name = self._getSettingTypeName(full_path)
                if type_name is not None:
                    logger.debug(f"Loading setting: {full_path} = {value} ({type_name})")
                    settings[key] = str2val(value, type_name)
                else:
                    logger.warning(f"Unknown setting: {full_path}")

    def _save(
        self      : Self,
        settings  : Dict,
        qsettings : QSettings,
        path      : str
    ) -> None:
        """Recursively save settings to QSettings."""
        for key, value in settings.items():
            if isinstance(value, dict):
                qsettings.beginGroup(key)
                self._save(value, qsettings, f"{path}/{key}")
                qsettings.endGroup()
            else:
                full_path = f"{path}/{key}"
                logger.debug(f"Saving setting: {full_path} = {value}")
                qsettings.setValue(key, val2str(value))

    def _toNamespace(self : Self, d : Dict) -> SimpleNamespace:
        """Convert a dictionary to a SimpleNamespace."""
        ns = SimpleNamespace()
        for key, value in d.items():
            if isinstance(value, dict):
                setattr(ns, key, self._toNamespace(value))
            else:
                setattr(ns, key, value)
        return ns

    def _dump(
        self   : Self,
        name   : str,
        x      : Any,
        lines  : List[str],
        indent : str = "  "
    ) -> None:
        """Recursively dump settings to a list of strings."""
        if isinstance(x, dict):
            for k, v in x.items():
                if isinstance(v, dict):
                    lines.append(f"{indent}{name}/{k}:")
                    self._dump(f"{name}/{k}", v, lines, indent + "  ")
                else:
                    lines.append(f"{indent}{name}/{k} = {val2str(v)}")
        else:
            lines.append(f"{indent}{name} = {val2str(x)}")
