"""
Settings management for the ConnectEd application.

This module provides classes for managing application settings,
including loading, saving, and accessing configuration values.
"""

# TODO:
# persistant settings for application
# session settings for diagram and library

from types  import SimpleNamespace
from typing import Self, Any

from importlib.resources import files
from pathlib import Path

import yaml

from PyQt6.QtCore import QObject, pyqtSignal, QSettings, QPointF

from ..app import logger

from .check   import checked
from .defs    import ORG_NAME, APP_NAME, DEFS
from .themes  import BUILTIN_THEMES, loadTheme
from .utils   import getDefaultPath, val2str, str2val


# Leaf path -> type name for app settings (from export of FACTORY_SETTINGS).
_APP_LEAF_KINDS : dict[str, str] = {
    "ai/chat_mru"                    : "str",
    "ai/confirm_destructive"         : "bool",
    "ai/default_profile"             : "str",
    "ai/max_tool_rounds"             : "int",
    "ai/profiles_data"               : "str",
    "ai/system_prompt_extra"         : "str",
    "defaults/border"                : "float",
    "defaults/grid/alpha"            : "int",
    "defaults/grid/display"          : "bool",
    "defaults/grid/dots"             : "bool",
    "defaults/grid/min_pixels"       : "int",
    "defaults/grid/snap"             : "bool",
    "defaults/margin"                : "float",
    "defaults/sheet/name"            : "str",
    "display/alpha"                  : "int",
    "display/font_size"              : "int",
    "display/pan/step"               : "float",
    "display/select/outline/style"   : "PenStyle",
    "display/select/outline/width"   : "int",
    "display/select/tolerance"       : "float",
    "display/theme"                  : "str",
    "display/zoom/max"               : "float",
    "display/zoom/min"               : "float",
    "display/zoom/padding"           : "float",
    "display/zoom/step"              : "float",
    "mru/1"                          : "str",
    "mru/2"                          : "str",
    "mru/3"                          : "str",
    "mru/4"                          : "str",
    "mru/5"                          : "str",
    "mru/6"                          : "str",
    "mru/7"                          : "str",
    "mru/8"                          : "str",
    "mru/9"                          : "str",
    "prefs/file/new/margin"          : "int",
    "prefs/file/new/sheet"           : "str",
    "prefs/file/open/dir"            : "str",
    "prefs/file/save/dir"            : "str",
    "prefs/mouse/drag"               : "int",
    "prefs/mouse/wheel"              : "int",
    "startup/geometry"               : "bytes",
    "ui/default/font/size"           : "int",
    "ui/navigator/font/size"         : "int",
}


def _resourcePath(relative : str) -> Path:
    try:
        base = files("ConnectEd.core")
        path = base / relative
        if path.is_file():
            return Path(str(path))
    except (ModuleNotFoundError, AttributeError, TypeError):
        pass
    core = Path(__file__).resolve().parent
    return core / relative


@checked
def _loadYaml(path : Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    if not isinstance(doc, dict):
        raise ValueError(f"Settings file {path} must be a mapping")
    return doc


def _coerceAppLeaves(
    d    : dict[str, Any],
    path : str,
) -> None:
    for key, value in d.items():
        child_path = f"{path}/{key}" if path else key
        if isinstance(value, dict):
            _coerceAppLeaves(value, child_path)
        elif child_path in _APP_LEAF_KINDS:
            kind = _APP_LEAF_KINDS[child_path]
            if kind == "bytes" and value == "":
                d[key] = b""
            else:
                d[key] = str2val(str(value), kind)


@checked
def _applyRuntimeDefaults(settings : dict[str, Any]) -> None:
    settings["startup"]["geometry"] = b""
    settings["prefs"]["file"]["open"]["dir"] = getDefaultPath()
    settings["prefs"]["file"]["save"]["dir"] = getDefaultPath()

    sheet_name = settings["defaults"]["sheet"]["name"]
    settings["defaults"]["sheet"]["size"] = DEFS["sheets"][sheet_name]

    pitch = settings["defaults"]["grid"]["pitch"]
    if isinstance(pitch, list):
        settings["defaults"]["grid"]["pitch"] = QPointF(
            float(pitch[0]), float(pitch[1])
        )


@checked
def loadFactorySettings() -> dict[str, Any]:
    base = _loadYaml(_resourcePath("settings.yaml"))
    _coerceAppLeaves(base, "")

    base["themes"] = {}
    for theme_id in BUILTIN_THEMES:
        tid, theme = loadTheme(
            _resourcePath(f"themes/{theme_id}.yaml"),
            theme_id,
        )
        base["themes"][tid] = theme

    _applyRuntimeDefaults(base)
    return base


FACTORY_SETTINGS = loadFactorySettings()


class Settings(QObject):
    # instance attributes
    _settings : dict[str, Any]

    # signals
    changed = pyqtSignal()
    mruChanged = pyqtSignal()

    @checked
    def __init__(self : Self) -> None:
        super().__init__()
        self._settings = self._deepCopy(FACTORY_SETTINGS)

    @checked
    def get(self : Self, path : str) -> Any:
        theme = self._get(self._settings, "display/theme")
        path = f"/{path}".replace("/theme/", f"/themes/{theme}/").strip("/")
        value = self._get(self._settings, path)
        return self._toNamespace(value) if isinstance(value, dict) else value

    @checked
    def getMRU(self : Self) -> list[str]:
        r = []
        for i in range(1, 10):
            mru = self.get(f"mru/{i}")
            if mru:
                r.append(mru)
        return r

    @checked
    def addMRU(self : Self, file_name : str) -> None:
        old_mru = self.getMRU()  # existing list
        new_mru = [file_name]
        for entry in old_mru:
            if entry != file_name:
                new_mru.append(entry)
        for i in range(1, 10):
            if i - 1 < len(new_mru):
                self.set(f"mru/{i}", new_mru[i - 1], emit=False)
            else:
                self.set(f"mru/{i}", "", emit=False)
        self.mruChanged.emit()

    @checked
    def set(self : Self, path : str, value : Any, emit : bool = True) -> None:
        tn = type(value).__name__
        tnx = self._getSettingKind(path) # type name expected
        if tn != tnx:
            logger().warning(
                f"Bad type for setting {path} - expected {tnx} but got {tn}"
            )
            return
        self._set(self._settings, path, value)
        if emit:
            self.changed.emit()

    @checked
    def reset(self : Self) -> None:
        """Clear all saved settings from QSettings."""
        logger().info("Clearing all persistent settings")
        qsettings = QSettings(ORG_NAME, APP_NAME)
        qsettings.clear()
        self._settings = self._deepCopy(FACTORY_SETTINGS)
        self.changed.emit()

    @checked
    def load(self : Self) -> None:
        """Load settings from QSettings into the settings store."""
        logger().debug("Loading settings")
        qsettings = QSettings(ORG_NAME, APP_NAME)
        for group in FACTORY_SETTINGS.keys():
            qsettings.beginGroup(group)
            self._load(self._settings[group], qsettings, group)
            qsettings.endGroup()
        self.changed.emit()

    @checked
    def save(self : Self) -> None:
        """Save settings to QSettings storage."""
        logger().debug("Saving settings")
        qsettings = QSettings(ORG_NAME, APP_NAME)
        for group, value in self._settings.items():
            qsettings.beginGroup(group)
            self._save(value, qsettings, group)
            qsettings.endGroup()

    @checked
    def dump(self : Self) -> str:
        """Return a formatted string representation of all settings."""
        lines: list[str] = []
        self._dump("settings", self._settings, lines)
        return "\n".join(lines)

    def _deepCopy(self : Self, d : dict) -> dict:
        """Create a deep copy of a settings dictionary."""
        result = {}
        for k, v in d.items():
            if isinstance(v, dict):
                result[k] = self._deepCopy(v)
            else:
                result[k] = v
        return result

    def _get(self : Self, d : dict, path : str) -> Any:
        """Retrieve a nested value from a dictionary by path."""
        path_parts = path.strip("/").split("/")
        current = d
        for part in path_parts:
            if not isinstance(current, dict) or part not in current:
                raise KeyError(f"Invalid settings path: {'/'.join(path_parts)}")
            current = current[part]
        return current

    def _set(self : Self, d : dict, path : str, value : Any) -> None:
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

    def _getSettingKind(self : Self, path : str) -> str | None:
        """Determine the expected type of a setting based on FACTORY_SETTINGS."""
        try:
            value = self._get(FACTORY_SETTINGS, path)
        except KeyError:
            return None
        return None if isinstance(value, dict) else type(value).__name__

    def _load(
        self      : Self,
        settings  : dict,
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
                kind = self._getSettingKind(full_path)
                if kind is not None:
                    logger().debug(f"Loading setting: {full_path} = {value} ({kind})")
                    settings[key] = str2val(str(value), kind)
                else:
                    logger().warning(f"Unknown setting: {full_path}")

    def _save(
        self      : Self,
        settings  : dict,
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

    def _toNamespace(self : Self, d : dict) -> SimpleNamespace:
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
        lines  : list[str],
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
