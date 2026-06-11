from pathlib import Path

import pytest
from PyQt6.QtGui import QColor

from ConnectEd.core.settings import loadFactorySettings
from ConnectEd.core.themes import loadTheme, resolvePresets


def _writeTheme(path : Path, text : str) -> None:
    path.write_text(text, encoding="utf-8")


_MINIMAL_PALETTE = """
palette:
  black   : '#000000'
  mid_grey : '#808080'
"""

_MINIMAL_PRESETS = """
  Background           : black
  Origin               : '#FFFFFF'
  Sheet                : '#FFFFFF'
  Border               : mid_grey
  Grid                 : '#404040'
  FreeNodeUnconnected  : '#FFFF00'
  FreeNodeConnected    : '#FFFF00'
  FreeNodeJunction     : '#FF0000'
  FixedNodeUnconnected : '#FFFF00'
  FixedNodeConnected   : '#FFFF00'
  FixedNodeJunction    : '#FF0000'
  SegmentUnresolved    : '#004000'
  SegmentScalar        : '#004000'
  SegmentVector        : '#004000'
  SegmentPreview1      : '#C000C0'
  SegmentPreview2      : '#800080'
  TapUnresolved        : '#404000'
  TapScalar            : '#004000'
  TapVector            : '#004000'
  NetLabel             : '#004040'
  PortPinWire          : '#808080'
  PortPinBus           : '#808080'
  PortArrowLine        : '#808080'
  PortArrowFill        : '#808000'
  PortName             : '#808000'
  PortComment          : '#808000'
  GateLine             : '#808080'
  GateFill             : '#404040'
  GatePinWire          : '#808080'
  GatePinBus           : '#808080'
  GatePinArrowLine     : '#808000'
  GatePinArrowFill     : '#808000'
  BlockLine            : '#808080'
  BlockFill            : '#404040'
  BlockLabel           : '#008080'
  BlockName            : '#008080'
  BlockPinWire         : '#808080'
  BlockPinBus          : '#808080'
  BlockPinArrowLine    : '#808000'
  BlockPinArrowFill    : '#808000'
  BlockPinName         : '#808000'
  BlockPinComment      : '#808000'
  SymbolPinWire        : '#808080'
  SymbolPinBus         : '#808080'
  SymbolPinArrowLine   : '#808000'
  SymbolPinArrowFill   : '#808000'
  SymbolPinName        : '#808000'
  SymbolPinComment     : '#808000'
  PropertyText         : '#800000'
  Junction             : '#C00000'
  Line                 : '#C0C0C0'
  Rectangle            : '#C0C0C0'
  Ellipse              : '#C0C0C0'
  PolyVtx              : '#C0C0C0'
  Polyline             : '#C0C0C0'
  Text                 : '#C0C0C0'
  SelectedLine         : '#FF00FF'
  SelectedFill         : '#FF00FF'
  SelectedText         : '#FF00FF'
  Grip                 : '#FF00FF'
  Rubber               : '#FFFF00'
  PropertyDeleted      : '#400000'
  PropertyChanged      : '#404000'
  PropertyAdded        : '#004000'
"""


def test_builtin_dark_theme_loads_with_palette() -> None:
    from ConnectEd.core.settings import _resourcePath

    tid, theme = loadTheme(_resourcePath("themes/dark.yaml"), "dark")
    assert tid == "dark"
    assert theme["background"] == QColor("#000000")


def test_builtin_light_mono_theme_loads_with_palette() -> None:
    from ConnectEd.core.settings import _resourcePath

    tid, theme = loadTheme(_resourcePath("themes/light_mono.yaml"), "light_mono")
    assert tid == "light_mono"
    assert theme["background"] == QColor("#000000")


def test_factory_settings_loads_both_paletted_themes() -> None:
    settings = loadFactorySettings()
    assert settings["themes"]["dark"]["background"] == QColor("#000000")
    assert settings["themes"]["light_mono"]["sheet"] == QColor("#A0A0A0")


def test_resolve_presets_palette_and_preset_refs() -> None:
    palette = {"black": "#000000", "accent": "#FF00FF"}
    presets = {
        "Background": "black",
        "SelectedLine": "accent",
        "Grip": "@SelectedLine",
    }
    resolved = resolvePresets(presets, palette, "test")
    assert resolved["Background"] == "#000000"
    assert resolved["Grip"] == "#FF00FF"


def test_load_theme_without_palette_still_works(tmp_path : Path) -> None:
    yaml_text = f"""meta:
  id           : test_plain
  display_name : Test
presets:
{_MINIMAL_PRESETS.replace("Background           : black", "Background           : '#000000'").replace("Border               : mid_grey", "Border               : '#808080'")}
background : '@Background'
"""
    path = tmp_path / "test_plain.yaml"
    _writeTheme(path, yaml_text)
    tid, theme = loadTheme(path)
    assert theme["background"] == QColor("#000000")


def test_unresolved_preset_reference_raises(tmp_path : Path) -> None:
    yaml_text = f"""meta:
  id           : test_cycle
  display_name : Test
{_MINIMAL_PALETTE}
presets:
{_MINIMAL_PRESETS.replace("PortPinBus           : '#808080'", "PortPinBus           : '@GateLine'").replace("GateLine             : '#808080'", "GateLine             : '@PortPinBus'")}
background : '@Background'
"""
    path = tmp_path / "test_cycle.yaml"
    _writeTheme(path, yaml_text)
    with pytest.raises(ValueError, match="unresolved preset references"):
        loadTheme(path)
