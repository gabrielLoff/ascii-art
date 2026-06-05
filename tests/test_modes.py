from pathlib import Path

from PIL import Image
import pytest

from cli_art.modes import edge_map, hue_map, linear_map, threshold_map
from cli_art.ascii import image_to_ascii_grid


def _ramp() -> str:
    return " .:-=+*#%@"


def _black_pixel() -> tuple[int, int, int]:
    return (0, 0, 0)


def _white_pixel() -> tuple[int, int, int]:
    return (255, 255, 255)


def test_linear_map_brightness() -> None:
    width, height = 10, 5
    img = Image.new("RGB", (width, height))
    for x in range(width):
        v = int(x / (width - 1) * 255)
        for y in range(height):
            img.putpixel((x, y), (v, v, v))

    active = _ramp()
    grid = linear_map(img, active)

    first_char = grid[0][0][0]
    last_char = grid[0][-1][0]
    assert active.index(first_char) < active.index(last_char)


def test_edge_map_detects_horizontal_edge() -> None:
    width, height = 10, 10
    img = Image.new("RGB", (width, height))
    for y in range(height):
        color = (0, 0, 0) if y < 5 else (255, 255, 255)
        for x in range(width):
            img.putpixel((x, y), color)

    active = _ramp()
    grid = edge_map(img, active)

    edge_row = grid[5]
    flat_top = grid[0]
    flat_bottom = grid[9]

    edge_magnitude = sum(active.index(c[0]) for c in edge_row)
    top_magnitude = sum(active.index(c[0]) for c in flat_top)
    bottom_magnitude = sum(active.index(c[0]) for c in flat_bottom)

    assert edge_magnitude > top_magnitude
    assert edge_magnitude > bottom_magnitude


def test_edge_map_blank_image() -> None:
    width, height = 10, 10
    img = Image.new("RGB", (width, height), _white_pixel())

    active = _ramp()
    grid = edge_map(img, active)

    for row in grid:
        for char, _ in row:
            assert active.index(char) == 0


def test_threshold_map_only_two_chars() -> None:
    width, height = 10, 10
    img = Image.new("RGB", (width, height))
    for x in range(width):
        v = int(x / (width - 1) * 255)
        for y in range(height):
            img.putpixel((x, y), (v, v, v))

    active = _ramp()
    grid = threshold_map(img, active)

    used = set()
    for row in grid:
        for char, _ in row:
            used.add(char)

    assert len(used) <= 2
    assert active[0] in used
    assert active[-1] in used


def test_threshold_map_all_black() -> None:
    width, height = 5, 5
    img = Image.new("RGB", (width, height), _black_pixel())

    active = _ramp()
    grid = threshold_map(img, active)

    for row in grid:
        for char, _ in row:
            assert char == active[0]


def test_threshold_map_all_white() -> None:
    width, height = 5, 5
    img = Image.new("RGB", (width, height), _white_pixel())

    active = _ramp()
    grid = threshold_map(img, active)

    for row in grid:
        for char, _ in row:
            assert char == active[-1]


def test_hue_map_different_hues() -> None:
    width, height = 2, 1
    img = Image.new("RGB", (width, height))
    img.putpixel((0, 0), (255, 0, 0))
    img.putpixel((1, 0), (0, 0, 255))

    active = _ramp()
    grid = hue_map(img, active)

    char0 = grid[0][0][0]
    char1 = grid[0][1][0]
    assert char0 != char1


def test_hue_map_all_same_hue() -> None:
    width, height = 5, 5
    img = Image.new("RGB", (width, height), (255, 0, 0))

    active = _ramp()
    grid = hue_map(img, active)

    chars = {grid[y][x][0] for y in range(height) for x in range(width)}
    assert len(chars) == 1


def test_unknown_mode_raises(tmp_path: Path) -> None:
    img_path = tmp_path / "test.png"
    Image.new("RGB", (10, 10), (128, 128, 128)).save(img_path)

    with pytest.raises(ValueError, match="Unknown mapping mode"):
        image_to_ascii_grid(img_path, mode="nope")


def test_linear_map_default_ramp() -> None:
    width, height = 10, 5
    img = Image.new("RGB", (width, height))
    for x in range(width):
        v = int(x / (width - 1) * 255)
        for y in range(height):
            img.putpixel((x, y), (v, v, v))

    grid = linear_map(img, _ramp())

    first_char = grid[0][0][0]
    last_char = grid[0][-1][0]
    assert _ramp().index(first_char) < _ramp().index(last_char)
