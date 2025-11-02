"""
Settings management for the ConnectEd application.

This module provides classes for managing application settings,
including loading, saving, and accessing configuration values.
"""

# TODO:
# persistant settings for application
# session settings for diagram and library

from types  import SimpleNamespace
from typing import Self, Any, Dict, List

from PyQt6.QtCore import Qt, QObject, pyqtSignal, QSettings, QPointF, QSizeF

from ..app import logger

from .defs    import ORG_NAME, APP_NAME, DEFS
from .utils   import getDefaultPath, val2str, str2val
from .palette import PaletteDark, PaletteLightMono


FACTORY_SETTINGS = {
    "startup" : {
        "geometry" : b''
    },
    "mru" : {
        "1" : "",
        "2" : "",
        "3" : "",
        "4" : "",
        "5" : "",
        "6" : "",
        "7" : "",
        "8" : "",
        "9" : ""
    },
    "display" : {
        "theme" : "dark",
        "font_size" : 10,
        "alpha" : 240,
        "select" : {
            "tolerance" : 2.0,
            "outline" : {
                "width" : 0,
                "style" : Qt.PenStyle.DotLine
            }
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
        "extents" : QSizeF(800.0, 600.0),
        "sheet" : {
            "name" : "A4 (landscape)",
            "size" : DEFS["sheets"]["A4 (landscape)"]
        },
        "margin" : 10.0,
        "border" : 1.0,
        "grid" : {
            "display"    : True,
            "snap"       : True,
            "pitch"      : QPointF(10.0, 10.0),
            "dots"       : False,
            "alpha"      : 128,
            "min_pixels" : 10
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
            "background" : PaletteDark.Background,
            "origin" : {
                "color" : PaletteDark.Origin,
                "size"  : 12
            },
            "sheet"      : PaletteDark.Sheet,
            "border"     : PaletteDark.Border,
            "items" : {
                "Port" : {
                    "line" : {
                        "color" : PaletteDark.PortLine,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteDark.PortFill,
                        "style" : Qt.BrushStyle.NoBrush
                    },
                    "size" : 8
                },
                "PortEntry" : {
                    "size" : 3,
                    "line" : {
                        "color" : PaletteDark.PortEntry,
                        "width" : 0,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteDark.PortEntry,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "PortName" : {
                    "text" : {
                        "color"     : PaletteDark.PortName,
                        "family"    : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "PortComment" : {
                    "text" : {
                        "color"     : PaletteDark.PortComment,
                        "family"    : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "Block" : {
                    "line" : {
                        "color" : PaletteDark.BlockLine,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteDark.BlockFill,
                        "style" : Qt.BrushStyle.SolidPattern
                    }
                },
                "BlockPin" : {
                    "line" : {
                        "color" : PaletteDark.BlockPin,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    }
                },
                "BlockPinArrow" : {
                    "line" : {
                        "color" : PaletteDark.BlockPinArrow,
                        "width" : 0,
                        "style" : Qt.PenStyle.NoPen
                    },
                    "fill" : {
                        "color" : PaletteDark.BlockPinArrow,
                        "style" : Qt.BrushStyle.SolidPattern
                    }
                },
                "BlockPinEntry" : {
                    "size" : 3,
                    "line" : {
                        "color" : PaletteDark.BlockPin,
                        "width" : 0,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteDark.BlockPin,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "BlockPinName" : {
                    "text" : {
                        "color"     : PaletteDark.BlockPinName,
                        "family"    : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "BlockPinComment" : {
                    "text" : {
                        "color"     : PaletteDark.BlockPinComment,
                        "family"    : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "SymbolPin" : {
                    "line" : {
                        "color" : PaletteDark.SymbolPin,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteDark.SymbolPin,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "SymbolPinArrow" : {
                    "line" : {
                        "color" : PaletteDark.SymbolPinArrow,
                        "width" : 0,
                        "style" : Qt.PenStyle.NoPen
                    },
                    "fill" : {
                        "color" : PaletteDark.SymbolPinArrow,
                        "style" : Qt.BrushStyle.SolidPattern
                    }
                },
                "SymbolPinEntry" : {
                    "size" : 3,
                    "line" : {
                        "color" : PaletteDark.SymbolPin,
                        "width" : 0,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteDark.SymbolPin,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "SymbolPinName" : {
                    "text" : {
                        "color"     : PaletteDark.SymbolPinName,
                        "family"    : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "SymbolPinComment" : {
                    "text" : {
                        "color"     : PaletteDark.SymbolPinComment,
                        "family"    : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "PropertyText" : {
                    "text" : {
                        "color"     : PaletteDark.PropertyText,
                        "family"    : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "Junction" : {
                    "size"  : 4,
                    "line" : {
                        "color" : PaletteDark.Junction,
                        "width" : 0,
                        "style" : Qt.PenStyle.NoPen
                    },
                    "fill" : {
                        "color" : PaletteDark.Junction,
                        "style" : Qt.BrushStyle.SolidPattern
                    }
                },
                "ConnSegPreview1" : {
                    "line" : {
                        "color" : PaletteDark.ConnSegPreview1,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    }
                },
                "ConnSegPreview2" : {
                    "line" : {
                        "color" : PaletteDark.ConnSegPreview2,
                        "width" : 1,
                        "style" : Qt.PenStyle.DashDotDotLine
                    }
                },
                "ConnVtx" : {
                    "visible" : True,
                    "size"    : 4,
                    "line" : {
                        "color" : PaletteDark.ConnVtx,
                        "width" : 0,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill"    : {
                        "color" : PaletteDark.ConnVtx,
                        "style" : Qt.BrushStyle.NoBrush
                    },
                },
                "ConnSeg" : {
                    "line" : {
                        "color" : PaletteDark.ConnSeg,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    }
                },
                "Line" : {
                    "line" : {
                        "color" : PaletteDark.Line,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    }
                },
                "Rectangle" : {
                    "line" : {
                        "color" : PaletteDark.Rectangle,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteDark.Rectangle,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "Ellipse" : {
                    "line" : {
                        "color" : PaletteDark.Ellipse,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteDark.Ellipse,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "Polyline" : {
                    "line" : {
                        "color" : PaletteDark.Polyline,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    }
                },
                "Text" : {
                    "text" : {
                        "color"     : PaletteDark.Text,
                        "family"    : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "TextBlock" : {
                    "text" : {
                        "color"     : PaletteDark.TextBlock,
                        "family"    : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
            },
            "selected" : {
                "line" : PaletteDark.SelectedLine,
                "fill" : PaletteDark.SelectedFill,
                "text" : PaletteDark.SelectedText
            },
            "grip" : {
                "size"  : 12,
                "color" : PaletteDark.Grip
            },
            "grid" : {
                "line" : PaletteDark.Grid
            }
        },
        "light_mono" : {
            "background" : PaletteLightMono.Background,
            "origin" : {
                "color" : PaletteLightMono.Origin,
                "size"  : 12
            },
            "sheet"      : PaletteLightMono.Sheet,
            "border"     : PaletteLightMono.Border,
            "items" : {
                "Port" : {
                    "line" : {
                        "color" : PaletteLightMono.PortLine,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteLightMono.PortFill,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "PortEntry" : {
                    "size" : 3,
                    "line" : {
                        "color" : PaletteLightMono.PortLine,
                        "width" : 0,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteLightMono.PortFill,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "PortName" : {
                    "text" : {
                        "color"     : PaletteLightMono.PortName,
                        "family"    : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "Block" : {
                    "line" : {
                        "color" : PaletteLightMono.BlockLine,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteLightMono.BlockFill,
                        "style" : Qt.BrushStyle.SolidPattern
                    }
                },
                "BlockPin" : {
                    "line" : {
                        "color" : PaletteLightMono.BlockPin,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    }
                },
                "BlockPinArrow" : {
                    "line" : {
                        "color" : PaletteLightMono.BlockPinArrow,
                        "width" : 0,
                        "style" : Qt.PenStyle.NoPen
                    },
                    "fill" : {
                        "color" : PaletteLightMono.BlockPinArrow,
                        "style" : Qt.BrushStyle.SolidPattern
                    }
                },
                "BlockPinEntry" : {
                    "size" : 3,
                    "line" : {
                        "color" : PaletteLightMono.BlockPin,
                        "width" : 0,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteLightMono.BlockPin,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "BlockPinName" : {
                    "text" : {
                        "color"     : PaletteLightMono.BlockPinName,
                        "family"    : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "BlockPinComment" : {
                    "text" : {
                        "color"     : PaletteLightMono.BlockPinComment,
                        "family"    : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "SymbolPin" : {
                    "line" : {
                        "color" : PaletteLightMono.SymbolPin,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteLightMono.SymbolPin,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "SymbolPinArrow" : {
                    "line" : {
                        "color" : PaletteLightMono.SymbolPinArrow,
                        "width" : 0,
                        "style" : Qt.PenStyle.NoPen
                    },
                    "fill" : {
                        "color" : PaletteLightMono.SymbolPinArrow,
                        "style" : Qt.BrushStyle.SolidPattern
                    }
                },
                "SymbolPinEntry" : {
                    "size" : 3,
                    "line" : {
                        "color" : PaletteLightMono.SymbolPin,
                        "width" : 0,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteLightMono.SymbolPin,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "SymbolPinName" : {
                    "text" : {
                        "color"     : PaletteLightMono.SymbolPinName,
                        "family"    : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "SymbolPinComment" : {
                    "text" : {
                        "color"     : PaletteLightMono.SymbolPinComment,
                        "family"    : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "PropertyText" : {
                    "text" : {
                        "color"     : PaletteLightMono.PropertyText,
                        "family"    : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "Junction" : {
                    "size"  : 4,
                    "line" : {
                        "color" : PaletteLightMono.Junction,
                        "width" : 0,
                        "style" : Qt.PenStyle.NoPen
                    },
                    "fill" : {
                        "color" : PaletteLightMono.Junction,
                        "style" : Qt.BrushStyle.SolidPattern
                    }
                },
                "ConnSegPreview1" : {
                    "line" : {
                        "color" : PaletteLightMono.ConnSegPreview1,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    }
                },
                "ConnSegPreview2" : {
                    "line" : {
                        "color" : PaletteLightMono.ConnSegPreview2,
                        "width" : 1,
                        "style" : Qt.PenStyle.DashDotDotLine
                    }
                },
                "ConnVtx" : {
                    "visible" : True,
                    "size"    : 4,
                    "line" : {
                        "color" : PaletteLightMono.ConnVtx,
                        "width" : 0,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill"    : {
                        "color" : PaletteLightMono.ConnVtx,
                        "style" : Qt.BrushStyle.NoBrush
                    },
                },
                "ConnSeg" : {
                    "line" : {
                        "color" : PaletteLightMono.ConnSeg,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    }
                },
                "Line" : {
                    "line" : {
                        "color" : PaletteLightMono.Line,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    }
                },
                "Rectangle" : {
                    "line" : {
                        "color" : PaletteLightMono.Rectangle,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteLightMono.Rectangle,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "Ellipse" : {
                    "line" : {
                        "color" : PaletteLightMono.Ellipse,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteLightMono.Ellipse,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "Polyline" : {
                    "line" : {
                        "color" : PaletteLightMono.Polyline,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    }
                },
                "Text" : {
                    "text" : {
                        "color"     : PaletteLightMono.Text,
                        "family"    : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "TextBlock" : {
                    "text" : {
                        "color"     : PaletteLightMono.TextBlock,
                        "family"    : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                }
            },
            "selected" : {
                "line" : PaletteLightMono.SelectedLine,
                "fill" : PaletteLightMono.SelectedFill,
                "text" : PaletteLightMono.SelectedText
            },
            "grip" : {
                "size"  : 12,
                "color" : PaletteLightMono.Grip
            },
            "grid" : {
                "line" : PaletteLightMono.Grid
            }
        }
    }
}

class Settings(QObject):
    # instance attributes
    _settings : dict[str, Any]

    # signals
    changed = pyqtSignal()
    mruChanged = pyqtSignal()

    def __init__(self : Self) -> None:
        super().__init__()
        self._settings = self._deepCopy(FACTORY_SETTINGS)

    def get(self : Self, path : str) -> Any:
        theme = self._get(self._settings, "display/theme")
        path = f"/{path}".replace("/theme/", f"/themes/{theme}/").strip("/")
        value = self._get(self._settings, path)
        return self._toNamespace(value) if isinstance(value, dict) else value

    def getMRU(self : Self) -> list[str]:
        r = []
        for i in range(1, 10):
            mru = self.get(f"mru/{i}")
            if mru:
                r.append(mru)
        return r

    def addMRU(self : Self, file_name : str) -> None:
        for i in range(1, 9):
            self.set(f"mru/{i+1}", self.get(f"mru/{i}"))
        self.set(f"mru/1", file_name)
        self.mruChanged.emit()

    def set(self : Self, path : str, value : Any, emit : bool = True) -> None:
        tn = type(value).__name__
        tnx = self._getSettingTypeName(path) # type name expected
        if tn != tnx:
            logger().warning(
                f"Bad type for setting {path} - expected {tnx} but got {tn}"
            )
            return
        self._set(self._settings, path, value)
        if emit:
            self.changed.emit()

    def reset(self : Self) -> None:
        """Clear all saved settings from QSettings."""
        logger().info("Clearing all persistent settings")
        qsettings = QSettings(ORG_NAME, APP_NAME)
        qsettings.clear()
        self._settings = self._deepCopy(FACTORY_SETTINGS)
        self.changed.emit()

    def load(self : Self) -> None:
        """Load settings from QSettings into the settings store."""
        logger().debug("Loading settings")
        qsettings = QSettings(ORG_NAME, APP_NAME)
        for group in FACTORY_SETTINGS.keys():
            qsettings.beginGroup(group)
            self._load(self._settings[group], qsettings, group)
            qsettings.endGroup()
        self.changed.emit()

    def save(self : Self) -> None:
        """Save settings to QSettings storage."""
        logger().debug("Saving settings")
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

    def _deepCopy(self : Self, d : Dict) -> Dict:
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

    def _getSettingTypeName(self : Self, path : str) -> str | None:
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
                    logger().debug(f"Loading setting: {full_path} = {value} ({type_name})")
                    settings[key] = str2val(value, type_name)
                else:
                    logger().warning(f"Unknown setting: {full_path}")

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
                logger().debug(f"Saving setting: {full_path} = {value}")
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
