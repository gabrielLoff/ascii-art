from pathlib import Path

from PIL import Image
from typer.testing import CliRunner

from cli_art.cli import app

runner = CliRunner()


def test_ascii(tmp_path: Path) -> None:
    img = Image.new("RGB", (30, 10), color=(255, 0, 0))
    for x in range(30):
        for y in range(10):
            img.putpixel((x, y), (int(x / 30 * 255), int(y / 10 * 255), 128))
    img_path = tmp_path / "test.png"
    img.save(img_path)

    result = runner.invoke(app, ["ascii", str(img_path)])
    assert result.exit_code == 0

    result = runner.invoke(app, ["ascii", str(img_path), "--invert"])
    assert result.exit_code == 0

    out_html = tmp_path / "out.html"
    result = runner.invoke(app, ["ascii", str(img_path), "--output", str(out_html)])
    assert result.exit_code == 0
    assert out_html.exists()
    assert out_html.stat().st_size > 0

    out_txt = tmp_path / "out.txt"
    result = runner.invoke(app, ["ascii", str(img_path), "--output", str(out_txt)])
    assert result.exit_code == 0
    assert out_txt.exists()
    assert out_txt.stat().st_size > 0


def test_ascii_file_not_found() -> None:
    result = runner.invoke(app, ["ascii", "/nonexistent/image.png"])
    assert result.exit_code != 0


def test_ascii_custom_chars(tmp_path: Path) -> None:
    img = Image.new("RGB", (30, 10), color=(255, 0, 0))
    for x in range(30):
        for y in range(10):
            img.putpixel((x, y), (int(x / 30 * 255), int(y / 10 * 255), 128))
    img_path = tmp_path / "test.png"
    img.save(img_path)

    result = runner.invoke(app, ["ascii", str(img_path), "--chars", "@%#*+=-:. "])
    assert result.exit_code == 0


def test_ascii_custom_chars_invert(tmp_path: Path) -> None:
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    img_path = tmp_path / "test.png"
    img.save(img_path)

    result = runner.invoke(app, ["ascii", str(img_path), "--chars", "@%#", "--invert"])
    assert result.exit_code == 0


def test_ascii_empty_chars_rejected(tmp_path: Path) -> None:
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    img_path = tmp_path / "test.png"
    img.save(img_path)

    result = runner.invoke(app, ["ascii", str(img_path), "--chars", ""])
    assert result.exit_code != 0


def test_ascii_single_char_ramp(tmp_path: Path) -> None:
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    img_path = tmp_path / "test.png"
    img.save(img_path)

    result = runner.invoke(app, ["ascii", str(img_path), "--chars", "@"])
    assert result.exit_code == 0


def test_ascii_unicode_chars(tmp_path: Path) -> None:
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    img_path = tmp_path / "test.png"
    img.save(img_path)

    result = runner.invoke(app, ["ascii", str(img_path), "--chars", " ░▒▓█"])
    assert result.exit_code == 0


def test_theme_valid(tmp_path: Path) -> None:
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    img_path = tmp_path / "test.png"
    img.save(img_path)

    result = runner.invoke(app, ["ascii", str(img_path), "--theme", "eighths"])
    assert result.exit_code == 0


def test_theme_invalid(tmp_path: Path) -> None:
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    img_path = tmp_path / "test.png"
    img.save(img_path)

    result = runner.invoke(app, ["ascii", str(img_path), "--theme", "nope"])
    assert result.exit_code != 0


def test_theme_and_chars_conflict(tmp_path: Path) -> None:
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    img_path = tmp_path / "test.png"
    img.save(img_path)

    result = runner.invoke(
        app, ["ascii", str(img_path), "--theme", "eighths", "--chars", "@%#"]
    )
    assert result.exit_code != 0


def test_theme_with_invert(tmp_path: Path) -> None:
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    img_path = tmp_path / "test.png"
    img.save(img_path)

    result = runner.invoke(app, ["ascii", str(img_path), "--theme", "eighths", "--invert"])
    assert result.exit_code == 0


def test_complete_theme_empty() -> None:
    from cli_art.cli import _complete_theme
    names = _complete_theme(None, "")
    assert names == sorted(["eighths", "vertical-bars", "quadrant",
                            "stippled", "halftone", "geometric", "mono"])


def test_complete_theme_partial() -> None:
    from cli_art.cli import _complete_theme
    assert _complete_theme(None, "ve") == ["vertical-bars"]
    assert _complete_theme(None, "e") == ["eighths"]
    assert _complete_theme(None, "mon") == ["mono"]


def test_complete_theme_no_match() -> None:
    from cli_art.cli import _complete_theme
    assert _complete_theme(None, "nope") == []


def test_themes_command() -> None:
    result = runner.invoke(app, ["themes"])
    assert result.exit_code == 0
    assert "eighths" in result.stdout
    assert "Available themes" in result.stdout


def test_ascii_url_success(tmp_path: Path) -> None:
    from unittest.mock import patch

    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    img_path = tmp_path / "test.png"
    img.save(img_path)

    with open(img_path, "rb") as f:
        png_data = f.read()

    class MockResp:
        def __init__(self) -> None:
            self.headers = {"Content-Length": str(len(png_data))}
            self._data = png_data
            self._pos = 0

        def read(self, size: int = -1) -> bytes:
            if size == -1:
                remaining = self._data[self._pos:]
                self._pos = len(self._data)
                return remaining
            chunk = self._data[self._pos:self._pos + size]
            self._pos += len(chunk)
            return chunk

        def close(self) -> None:
            pass

    with patch("urllib.request.urlopen", return_value=MockResp()):
        result = runner.invoke(app, ["ascii", "https://example.com/test.png"])
    assert result.exit_code == 0


def test_ascii_url_download_fails() -> None:
    from unittest.mock import patch
    import urllib.error

    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("Connection refused")):
        result = runner.invoke(app, ["ascii", "https://example.com/test.png"])
    assert result.exit_code != 0
