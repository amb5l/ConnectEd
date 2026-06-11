from dataclasses import fields

from ..check import checked
from ..palette import ThemePalette


PRESET_TOKENS : frozenset[str] = frozenset(
    f.name for f in fields(ThemePalette)
)


@checked
def validatePalette(theme_name : str, palette : dict[str, str]) -> None:
    for name, value in palette.items():
        if not isinstance(value, str) or not value.startswith("#"):
            raise ValueError(
                f"Theme {theme_name!r} palette {name!r} must be #RRGGBB, "
                f"got {value!r}"
            )


@checked
def validatePresetSources(
    theme_name   : str,
    presets      : dict[str, str],
    palette_keys : frozenset[str],
) -> None:
    for name, value in presets.items():
        if not isinstance(value, str):
            raise ValueError(
                f"Theme {theme_name!r} preset {name!r} must be a string, "
                f"got {type(value).__name__}"
            )
        if value.startswith("#"):
            continue
        if value.startswith("@"):
            token = value[1:]
            if token not in presets:
                raise ValueError(
                    f"Theme {theme_name!r} preset {name!r} references "
                    f"unknown preset {token!r}"
                )
            continue
        if value in palette_keys:
            continue
        raise ValueError(
            f"Theme {theme_name!r} preset {name!r} must be #RRGGBB, "
            f"@Preset, or a palette name, got {value!r}"
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
