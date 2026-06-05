import colorsys

from PIL import Image

AsciiGrid = list[list[tuple[str, tuple[int, int, int]]]]


def _build_lut(active: str) -> list[int]:
    return [int(i / 255 * (len(active) - 1)) for i in range(256)]


def _build_threshold_lut(active: str) -> list[int]:
    last = len(active) - 1
    return [0 if i < 128 else last for i in range(256)]


def _pixels_data(img: Image.Image) -> list:
    """Return pixel data as a flat list (list of tuples for RGB, list of ints for L)."""
    return list(img.get_flattened_data())


def linear_map(img: Image.Image, active: str) -> AsciiGrid:
    width, height = img.size
    pixels = _pixels_data(img)
    gray = img.convert("L")
    char_indices = _pixels_data(gray.point(_build_lut(active)))

    grid: AsciiGrid = []
    for y in range(height):
        offset = y * width
        row = [(active[char_indices[offset + x]], pixels[offset + x]) for x in range(width)]
        grid.append(row)

    return grid


def threshold_map(img: Image.Image, active: str) -> AsciiGrid:
    width, height = img.size
    pixels = _pixels_data(img)
    gray = img.convert("L")
    char_indices = _pixels_data(gray.point(_build_threshold_lut(active)))

    grid: AsciiGrid = []
    for y in range(height):
        offset = y * width
        row = [(active[char_indices[offset + x]], pixels[offset + x]) for x in range(width)]
        grid.append(row)

    return grid


def hue_map(img: Image.Image, active: str) -> AsciiGrid:
    width, height = img.size
    pixels = _pixels_data(img)
    ramp_len = len(active)

    grid: AsciiGrid = []
    for y in range(height):
        row: list[tuple[str, tuple[int, int, int]]] = []
        offset = y * width
        for x in range(width):
            r, g, b = pixels[offset + x]
            h, _s, _v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            char_idx = int(h * (ramp_len - 1))
            row.append((active[char_idx], (r, g, b)))
        grid.append(row)

    return grid


def edge_map(img: Image.Image, active: str) -> AsciiGrid:
    gray = img.convert("L")
    width, height = img.size
    pixels = _pixels_data(img)
    gray_data = _pixels_data(gray)
    ramp_len = len(active)

    grid: AsciiGrid = []
    for y in range(height):
        row: list[tuple[str, tuple[int, int, int]]] = []
        for x in range(width):
            if x == 0 or x >= width - 1 or y == 0 or y >= height - 1:
                magnitude = 0
            else:
                idx = y * width + x
                gx = (
                    -gray_data[idx - width - 1] + gray_data[idx - width + 1]
                    + -2 * gray_data[idx - 1] + 2 * gray_data[idx + 1]
                    + -gray_data[idx + width - 1] + gray_data[idx + width + 1]
                )
                gy = (
                    -gray_data[idx - width - 1] + -2 * gray_data[idx - width] + -gray_data[idx - width + 1]
                    + gray_data[idx + width - 1] + 2 * gray_data[idx + width] + gray_data[idx + width + 1]
                )
                magnitude = min(255, int((gx * gx + gy * gy) ** 0.5))
            char_idx = int(magnitude / 255 * (ramp_len - 1))
            r, g, b = pixels[y * width + x]
            row.append((active[char_idx], (r, g, b)))
        grid.append(row)

    return grid
