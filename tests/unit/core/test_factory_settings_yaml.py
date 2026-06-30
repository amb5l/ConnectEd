from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor

from ConnectEd.core.defs import DEFS
from ConnectEd.core.settings import FACTORY_SETTINGS, Settings, loadFactorySettings
from ConnectEd.core.themes import BUILTIN_THEMES, THEME_NAMES, resolveColor


def test_load_factory_settings_top_level_keys() -> None:
    settings = loadFactorySettings()
    assert set(settings.keys()) == {
        "startup", "mru", "ui", "display", "defaults", "prefs", "ai", "themes",
    }


def test_builtin_theme_names() -> None:
    assert THEME_NAMES == frozenset({"dark", "light_mono"})
    assert BUILTIN_THEMES == ("dark", "light_mono")


def test_theme_token_resolves_to_palette_color() -> None:
    settings = loadFactorySettings()
    bg = settings["themes"]["dark"]["background"]
    assert isinstance(bg, QColor)
    assert bg == QColor("#000000")


def test_resolve_color_inline_hex() -> None:
    presets = {"Background": "#000000"}
    color = resolveColor("#008080", presets, "test")
    assert color.red() == 0
    assert color.green() == 128
    assert color.blue() == 128


def test_runtime_defaults() -> None:
    settings = loadFactorySettings()
    assert settings["startup"]["geometry"] == b""
    assert settings["prefs"]["file"]["open"]["dir"]
    sheet_name = settings["defaults"]["sheet"]["name"]
    assert settings["defaults"]["sheet"]["size"] == DEFS["sheets"][sheet_name]
    assert "extents" not in settings["defaults"]
    assert isinstance(settings["defaults"]["grid"]["pitch"], QPointF)


def test_settings_get_smoke() -> None:
    factory = loadFactorySettings()
    store = Settings()
    assert store.get("display/theme") == "dark"
    assert store.get("defaults/sheet/name") == "A4 (landscape)"
    block_color = store.get("theme/items/BlockName/text/color")
    assert isinstance(block_color, QColor)
    expected = factory["themes"]["dark"]["items"]["BlockName"]["text"]["color"]
    assert block_color == expected


def test_factory_settings_matches_loader() -> None:
    assert set(FACTORY_SETTINGS.keys()) == set(loadFactorySettings().keys())


def test_segment_line_style_is_pen_style() -> None:
    style = loadFactorySettings()["themes"]["dark"]["items"]["Segment"]["line"][
        "scalar"
    ]["style"]
    assert style == Qt.PenStyle.SolidLine
    assert isinstance(style, Qt.PenStyle)
