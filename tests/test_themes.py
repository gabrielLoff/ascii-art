import pytest

from cli_art.ascii import CHARS
from cli_art.themes import THEMES, resolve_chars


def test_resolve_chars_only_chars() -> None:
    assert resolve_chars(chars="@%#", theme=None) == "@%#"


def test_resolve_chars_only_theme() -> None:
    assert resolve_chars(chars=None, theme="eighths") == THEMES["eighths"]


def test_resolve_chars_neither() -> None:
    assert resolve_chars(chars=None, theme=None) == CHARS


def test_resolve_chars_both() -> None:
    with pytest.raises(ValueError, match="mutually exclusive"):
        resolve_chars(chars="@%#", theme="eighths")


def test_resolve_chars_bad_theme() -> None:
    with pytest.raises(ValueError, match="Unknown theme"):
        resolve_chars(chars=None, theme="nope")


def test_resolve_chars_empty_string_is_not_a_theme() -> None:
    with pytest.raises(ValueError, match="Unknown theme"):
        resolve_chars(chars=None, theme="")


def test_themes_dict_has_expected_keys() -> None:
    expected = {
        "eighths", "vertical-bars", "quadrant", "stippled", "halftone", "geometric", "mono",
        "braille", "shade-blocks", "classic", "numerical",
    }
    assert set(THEMES) == expected


def test_all_theme_chars_are_single_codepoints() -> None:
    for name, ramp in THEMES.items():
        for char in ramp:
            assert len(char) == 1, f"Theme '{name}' has multi-codepoint char {char!r}"
