"""
Settings management for the ConnectEd application.

This module provides classes for managing application settings,
including loading, saving, and accessing configuration values.
"""

# TODO:
# persistant settings for application
# session settings for diagram and library

__all__ = ["Settings"]

from types       import SimpleNamespace
from typing      import Self, Any, Dict, List

from PyQt6.QtCore import QSettings, QPointF, QSizeF, Qt
from PyQt6.QtGui  import QColor

from .log   import logger
from .defs  import ORG_NAME, APP_NAME
from .utils import getDefaultPath, val2str, str2val, MinMax


FACTORY_SETTINGS = {
    "startup" : {
        "geometry" : ""
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
        "display" : {
            "theme" : "dark",
            "elements" : {
                "rectangle" : {
                    "line" : {
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : Qt.BrushStyle.SolidPattern
                },
                "text" : {
                    "font" : {
                        "family"    : "Arial",
                        "size"      : 12,
                        "weight"    : 400,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "selected" : {
                    "line" : {
                        "width" : 1,
                        "style" : Qt.PenStyle.DotLine
                    },
                    "fill" : Qt.BrushStyle.DiagCrossPattern,
                    "grip" : {
                        "size" : 4
                    }
                },
                "wip" : {
                    "line" : {
                        "width" : 0,
                        "style" : Qt.PenStyle.DashLine
                    },
                    "fill" : Qt.BrushStyle.NoBrush
                },
                "alpha" : 192
            },
            "zoom" : {
                "padding" : 0.1,
                "step"    : 0.25,
                "limit"   : MinMax(0.01, 100.0)
            },
            "pan" : {
                "step" : 0.1
            },
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
            "rectangle" : {
                "line" : QColor( 192, 120,   0 ), # light orange
                "fill" : QColor(  96, 100,   0 )  # dark orange
            },
            "text" : {
                "text" : QColor( 255, 255, 255 )
            },
            "wip" : {
                "line" : QColor(   0, 255,   0 ), # bright green
                "fill" : QColor(   0, 128,   0 ), # medium green
                "text" : QColor(   0, 255,   0 )  # bright green
            },
            "selected" : {
                "line" : QColor( 255,   0, 255 ), # bright magenta
                "fill" : QColor( 255,   0, 255 ), # bright magenta
                "text" : QColor( 255,   0, 255 )  # bright magenta
            },
            "grip" : {
                "line" : QColor( 255,   0, 255 ), # bright magenta
                "fill" : QColor( 255,   0,   0 )  # bright red

            },
            "anchor" : {
                "line" : QColor( 255,   0, 255 ), # bright magenta
                "fill" : QColor( 255, 255, 128 )  # bright yellow
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
            "wip" : {
                "line" : QColor(   0, 255,   0 ), # bright green
                "fill" : QColor(   0, 128,   0 )  # medium green
            },
            "selected" : {
                "line" : QColor( 255,   0, 255 ), # bright magenta
                "fill" : QColor( 128,   0, 128 )  # medium magenta
            },
            "grip" : {
                "line" : QColor( 255,   0, 255 ), # bright magenta
                "fill" : QColor( 255, 255, 128 )  # bright yellow
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
    },
    "defaults" : { # TODO move these to session settings
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
        }
    }
}

class Settings(SimpleNamespace):
    @property
    def theme(self : Self) -> SimpleNamespace:
        return getattr(self.themes, self.prefs.display.theme)

    def __init__(self : Self) -> None:
        self._init(self, FACTORY_SETTINGS)

    def reset(self : Self) -> None:
        logger.debug("clearing all saved settings")
        qsettings = QSettings(ORG_NAME, APP_NAME)
        qsettings.clear()

    def load(self : Self) -> None:
        """Load settings from QSettings storage into this SimpleNamespace."""
        logger.debug("loading settings")
        qsettings = QSettings(ORG_NAME, APP_NAME)
        for attr_name in FACTORY_SETTINGS.keys():
            attr = getattr(self, attr_name)
            logger.debug(f"Loading settings for {attr_name}")
            qsettings.beginGroup(attr_name)
            self._load(attr, qsettings)
            qsettings.endGroup()

    def save(self : Self) -> None:
        """Save settings from this SimpleNamespace to QSettings storage."""
        logger.debug("saving settings")
        qsettings = QSettings(ORG_NAME, APP_NAME)
        for attr_name in FACTORY_SETTINGS.keys():
            attr = getattr(self, attr_name)
            logger.debug(f"Saving settings for {attr_name}")
            qsettings.beginGroup(attr_name)
            self._save(attr, qsettings)
            qsettings.endGroup()

    def dump(self : Self) -> str:
        """Return a formatted string representation of all settings."""
        lines: List[str] = []
        self._dump("settings", self, lines)
        return "\n".join(lines)

    def _getSettingTypeName(
        self : Self,
        path : str,
        d    : dict
    ) -> str:
        l = path.lstrip("/").split("/")
        if len(l) == 1 and l[0] in d and not isinstance(d[l[0]], dict):
            return type(d[l[0]]).__name__
        elif len(l) > 1 and isinstance(d[l[0]], dict):
            return self._getSettingTypeName("/"+"/".join(l[1:]), d[l[0]])
        return None

    def _init(
        self     : Self,
        ns       : SimpleNamespace,
        settings : Dict[str, Any] | Any
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
        self      : Self,
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
                path = f"/{qsettings.group()}/{key}"
                stype = self._getSettingTypeName(path, FACTORY_SETTINGS)
                if stype is not None:
                    logger.debug(f"loading setting: {path} = {value} ({stype})")
                    setattr(ns, key, str2val(value, stype))
                else:
                    logger.warning(f"Unknown setting: {path}")

    def _save(
        self      : Self,
        ns        : SimpleNamespace,
        qsettings : QSettings
    ) -> None:
        """Recursively save settings from a SimpleNamespace to QSettings."""
        for key, value in vars(ns).items():
            if not key.startswith("_") and not callable(value):
                if isinstance(value, SimpleNamespace):
                    qsettings.beginGroup(key)
                    path = f"/{qsettings.group()}"
                    logger.debug(f"saving settings group: {path}")
                    self._save(value, qsettings)
                    qsettings.endGroup()
                else:
                    path = f"/{qsettings.group()}/{key}"
                    logger.debug(f"saving setting: {path} = {value}")
                    qsettings.setValue(key, val2str(value))

    def _dump(
        self   : Self,
        name   : str,
        x      : Any,
        lines  : list[str],
        indent : str = "  "
    ) -> None:
        if isinstance(x, SimpleNamespace):
            for k, v in vars(x).items():
                if isinstance(v, SimpleNamespace):
                    lines.append(f"{indent}{name}/{k}:")
                    self._dump(name + "/" + k, v, lines, indent + "  ")
                else:
                    lines.append(f"{indent}{name}/{k} = {val2str(v)}")
        else:
            lines.append(f"{indent}{name} = {val2str(x)}")

settings = Settings()
