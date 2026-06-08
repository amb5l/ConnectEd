from dataclasses import fields

from ..check import checked
from ..palette import ThemePalette


PRESET_TOKENS : frozenset[str] = frozenset(
    f.name for f in fields(ThemePalette)
)


@checked
def validatePresets(theme_name : str, presets : dict[str, str]) -> None:
    missing = PRESET_TOKENS - presets.keys()
    if missing:
        raise ValueError(
            f"Theme {theme_name!r} missing presets: {sorted(missing)}"
        )
    extra = presets.keys() - PRESET_TOKENS
    if extra:
        raise ValueError(
            f"Theme {theme_name!r} unknown presets: {sorted(extra)}"
        )
    for name, value in presets.items():
        if not isinstance(value, str) or not value.startswith("#"):
            raise ValueError(
                f"Theme {theme_name!r} preset {name!r} must be #RRGGBB, "
                f"got {value!r}"
            )
