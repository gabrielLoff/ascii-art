from pathlib import Path
from unittest.mock import patch

from PIL import Image
from typer.testing import CliRunner

from cli_art.animate import (
    extract_frames,
    frames_to_grids,
    play_ansi_animation,
    render_html_animation,
)
from cli_art.cli import app

runner = CliRunner()


def test_extract_frames_count(two_frame_gif: Path) -> None:
    frames = extract_frames(two_frame_gif)
    assert len(frames) == 2


def test_extract_frames_single(single_frame_gif: Path) -> None:
    frames = extract_frames(single_frame_gif)
    assert len(frames) == 1


def test_extract_frames_static_png(gradient_png: Path) -> None:
    frames = extract_frames(gradient_png)
    assert len(frames) == 1


def test_extract_frames_delays(two_frame_gif: Path) -> None:
    frames = extract_frames(two_frame_gif)
    assert len(frames) == 2
    assert frames[0][1] >= 20
    assert frames[1][1] >= 20


def test_extract_frames_max_frames(two_frame_gif: Path) -> None:
    frames = extract_frames(two_frame_gif, max_frames=1)
    assert len(frames) == 1


def test_extract_frames_rgb(two_frame_gif: Path) -> None:
    frames = extract_frames(two_frame_gif)
    for frame, _ in frames:
        assert frame.mode == "RGB"


def test_frames_to_grids_shape(two_frame_gif: Path) -> None:
    frames = extract_frames(two_frame_gif)
    animated = frames_to_grids(frames, width=30, active=" .:-=+*#%@", mode="linear")
    assert len(animated) == 2
    for grid, delay in animated:
        assert len(grid) > 0
        assert len(grid[0]) > 0
        assert delay >= 20


def test_frames_to_grids_all_modes(two_frame_gif: Path) -> None:
    frames = extract_frames(two_frame_gif)
    for mode in ("linear", "edge", "threshold", "color-to-char"):
        animated = frames_to_grids(frames, width=30, active=" .:-=+*#%@", mode=mode)
        assert len(animated) == 2


def test_render_html_animation_structure(two_frame_gif: Path) -> None:
    frames = extract_frames(two_frame_gif)
    animated = frames_to_grids(frames, width=30, active=" .:-=+*#%@", mode="linear")
    html = render_html_animation(animated, fps=10)
    assert "<!DOCTYPE html>" in html
    assert "<script>" in html
    assert "setInterval" in html
    assert "var frames" in html


def test_render_html_animation_frame_count(two_frame_gif: Path) -> None:
    frames = extract_frames(two_frame_gif)
    animated = frames_to_grids(frames, width=30, active=" .:-=+*#%@", mode="linear")
    html = render_html_animation(animated, fps=10)
    assert "var frames = [" in html
    assert html.count("var frames") == 1


def test_render_html_animation_delay(two_frame_gif: Path) -> None:
    frames = extract_frames(two_frame_gif)
    animated = frames_to_grids(frames, width=30, active=" .:-=+*#%@", mode="linear")
    html = render_html_animation(animated, fps=20)
    assert "50" in html  # 1000/20 = 50ms


def test_render_html_animation_xss_escape() -> None:
    from cli_art.animate import _escape_js
    assert _escape_js("hello") == "hello"
    assert _escape_js("a`b") == "a\\`b"
    assert _escape_js("a${b") == "a\\${b"
    assert _escape_js("a\\b") == "a\\\\b"
    assert _escape_js("`${}\\") == "\\`\\${}\\\\"


def test_animate_basic(two_frame_gif: Path) -> None:
    with patch("time.sleep"):
        result = runner.invoke(app, ["animate", str(two_frame_gif)])
    assert result.exit_code == 0


def test_animate_html_output(tmp_path: Path, two_frame_gif: Path) -> None:
    out = tmp_path / "out.html"
    with patch("time.sleep"):
        result = runner.invoke(app, ["animate", str(two_frame_gif), "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content


def test_animate_with_options(two_frame_gif: Path) -> None:
    with patch("time.sleep"):
        result = runner.invoke(
            app, ["animate", str(two_frame_gif), "--width", "40", "--mode", "edge", "--fps", "15"]
        )
    assert result.exit_code == 0


def test_animate_no_color(two_frame_gif: Path) -> None:
    with patch("time.sleep"):
        result = runner.invoke(app, ["animate", str(two_frame_gif), "--no-color"])
    assert result.exit_code == 0
    assert "\033[" not in result.stdout


def test_animate_file_not_found() -> None:
    result = runner.invoke(app, ["animate", "/nonexistent/image.gif"])
    assert result.exit_code != 0


def test_animate_svg_rejected(tmp_path: Path, two_frame_gif: Path) -> None:
    out = tmp_path / "out.svg"
    result = runner.invoke(app, ["animate", str(two_frame_gif), "--output", str(out)])
    assert result.exit_code != 0


def test_animate_max_frames(two_frame_gif: Path) -> None:
    with patch("time.sleep"):
        result = runner.invoke(app, ["animate", str(two_frame_gif), "--max-frames", "1"])
    assert result.exit_code == 0


def test_animate_single_frame(single_frame_gif: Path) -> None:
    with patch("time.sleep"):
        result = runner.invoke(app, ["animate", str(single_frame_gif)])
    assert result.exit_code == 0


def test_animate_with_theme(two_frame_gif: Path) -> None:
    with patch("time.sleep"):
        result = runner.invoke(app, ["animate", str(two_frame_gif), "--theme", "eighths"])
    assert result.exit_code == 0


def test_animate_invert(two_frame_gif: Path) -> None:
    with patch("time.sleep"):
        result = runner.invoke(app, ["animate", str(two_frame_gif), "--invert"])
    assert result.exit_code == 0
