from pathlib import Path

from PIL import Image
from typer.testing import CliRunner

from cli_art.cli import app

from .conftest import MockResponse

runner = CliRunner()


def test_ascii(tmp_path: Path, gradient_png: Path) -> None:
    result = runner.invoke(app, ["ascii", str(gradient_png)])
    assert result.exit_code == 0

    result = runner.invoke(app, ["ascii", str(gradient_png), "--invert"])
    assert result.exit_code == 0

    out_html = tmp_path / "out.html"
    result = runner.invoke(app, ["ascii", str(gradient_png), "--output", str(out_html)])
    assert result.exit_code == 0
    assert out_html.exists()
    assert out_html.stat().st_size > 0

    out_txt = tmp_path / "out.txt"
    result = runner.invoke(app, ["ascii", str(gradient_png), "--output", str(out_txt)])
    assert result.exit_code == 0
    assert out_txt.exists()
    assert out_txt.stat().st_size > 0


def test_ascii_file_not_found() -> None:
    result = runner.invoke(app, ["ascii", "/nonexistent/image.png"])
    assert result.exit_code != 0


def test_ascii_custom_chars(gradient_png: Path) -> None:
    result = runner.invoke(app, ["ascii", str(gradient_png), "--chars", "@%#*+=-:. "])
    assert result.exit_code == 0


def test_ascii_custom_chars_invert(small_red_png: Path) -> None:
    result = runner.invoke(app, ["ascii", str(small_red_png), "--chars", "@%#", "--invert"])
    assert result.exit_code == 0


def test_ascii_empty_chars_rejected(small_red_png: Path) -> None:
    result = runner.invoke(app, ["ascii", str(small_red_png), "--chars", ""])
    assert result.exit_code != 0


def test_ascii_single_char_ramp(small_red_png: Path) -> None:
    result = runner.invoke(app, ["ascii", str(small_red_png), "--chars", "@"])
    assert result.exit_code == 0


def test_ascii_unicode_chars(small_red_png: Path) -> None:
    result = runner.invoke(app, ["ascii", str(small_red_png), "--chars", " ░▒▓█"])
    assert result.exit_code == 0


def test_theme_valid(small_red_png: Path) -> None:
    result = runner.invoke(app, ["ascii", str(small_red_png), "--theme", "eighths"])
    assert result.exit_code == 0


def test_theme_invalid(small_red_png: Path) -> None:
    result = runner.invoke(app, ["ascii", str(small_red_png), "--theme", "nope"])
    assert result.exit_code != 0


def test_theme_and_chars_conflict(small_red_png: Path) -> None:
    result = runner.invoke(
        app, ["ascii", str(small_red_png), "--theme", "eighths", "--chars", "@%#"]
    )
    assert result.exit_code != 0


def test_theme_with_invert(small_red_png: Path) -> None:
    result = runner.invoke(app, ["ascii", str(small_red_png), "--theme", "eighths", "--invert"])
    assert result.exit_code == 0


def test_complete_theme_empty() -> None:
    from cli_art.cli import _complete_theme
    names = _complete_theme(None, "")
    assert names == sorted(["eighths", "vertical-bars", "quadrant",
                            "stippled", "halftone", "geometric", "mono",
                            "braille", "shade-blocks", "classic", "numerical"])


def test_complete_theme_partial() -> None:
    from cli_art.cli import _complete_theme
    assert _complete_theme(None, "ve") == ["vertical-bars"]
    assert _complete_theme(None, "e") == ["eighths"]
    assert _complete_theme(None, "mon") == ["mono"]
    assert _complete_theme(None, "br") == ["braille"]
    assert _complete_theme(None, "cl") == ["classic"]


def test_complete_theme_no_match() -> None:
    from cli_art.cli import _complete_theme
    assert _complete_theme(None, "nope") == []


def test_themes_command() -> None:
    result = runner.invoke(app, ["themes"])
    assert result.exit_code == 0
    assert "eighths" in result.stdout
    assert "braille" in result.stdout
    assert "Available themes" in result.stdout


def test_ascii_url_success(small_red_png: Path) -> None:
    from unittest.mock import patch

    png_data = small_red_png.read_bytes()

    with patch("urllib.request.urlopen", return_value=MockResponse(
        png_data, {"Content-Length": str(len(png_data))}
    )):
        result = runner.invoke(app, ["ascii", "https://example.com/test.png"])
    assert result.exit_code == 0


def test_ascii_url_download_fails() -> None:
    from unittest.mock import patch
    import urllib.error

    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("Connection refused")):
        result = runner.invoke(app, ["ascii", "https://example.com/test.png"])
    assert result.exit_code != 0


def test_default_width_returns_terminal_columns() -> None:
    import os
    from unittest.mock import patch

    from cli_art.cli import _default_width

    cases = [
        (os.terminal_size((120, 24)), 120),
        (os.terminal_size((80, 24)), 80),
        (os.terminal_size((200, 50)), 200),
    ]
    for size, expected in cases:
        with patch("shutil.get_terminal_size", return_value=size):
            assert _default_width() == expected


def test_render_svg_basic() -> None:
    from cli_art.ascii import render_svg

    grid = [
        [("@", (255, 0, 0)), ("#", (0, 255, 0))],
        [(".", (0, 0, 255)), (" ", (128, 128, 128))],
    ]
    svg = render_svg(grid)
    assert svg.startswith('<?xml')
    assert '<svg' in svg
    assert '</svg>' in svg
    assert 'rgb(255,0,0)' in svg
    assert 'rgb(0,255,0)' in svg
    assert 'rgb(0,0,255)' in svg
    assert 'monospace' in svg
    assert '#000' in svg


def test_render_svg_empty_grid() -> None:
    from cli_art.ascii import render_svg

    svg = render_svg([])
    assert '<svg' in svg
    assert '</svg>' in svg


def test_render_svg_xml_escaping() -> None:
    from cli_art.ascii import render_svg

    grid = [[("<", (255, 0, 0)), (">", (0, 0, 0)), ("&", (128, 128, 128))]]
    svg = render_svg(grid)
    assert "&lt;" in svg
    assert "&gt;" in svg
    assert "&amp;" in svg


def test_ascii_svg_output(tmp_path: Path, gradient_png: Path) -> None:
    out_svg = tmp_path / "out.svg"
    result = runner.invoke(app, ["ascii", str(gradient_png), "--output", str(out_svg)])
    assert result.exit_code == 0
    assert out_svg.exists()
    assert out_svg.stat().st_size > 0

    content = out_svg.read_text(encoding="utf-8")
    assert '<svg' in content
    assert '</svg>' in content
    assert 'monospace' in content


def test_explicit_width_overrides_default(tmp_path: Path) -> None:
    img = Image.new("RGB", (100, 20), color=(255, 0, 0))
    img_path = tmp_path / "test.png"
    img.save(img_path)

    result_wide = runner.invoke(app, ["ascii", str(img_path), "--width", "120"])
    result_narrow = runner.invoke(app, ["ascii", str(img_path), "--width", "20"])

    assert result_wide.exit_code == 0
    assert result_narrow.exit_code == 0
    assert len(result_wide.stdout) > len(result_narrow.stdout)
