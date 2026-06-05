import colorsys

from PIL import Image

AsciiGrid = list[list[tuple[str, tuple[int, int, int]]]]


def linear_map(img: Image.Image, active: str) -> AsciiGrid:
    width, height = img.size
    pixels = img.load()

    grid: AsciiGrid = []
    for y in range(height):
        row: list[tuple[str, tuple[int, int, int]]] = []
        for x in range(width):
            r, g, b = pixels[x, y]
            brightness = (r + g + b) / 3
            char_idx = int(brightness / 255 * (len(active) - 1))
            row.append((active[char_idx], (r, g, b)))
        grid.append(row)

    return grid


def threshold_map(img: Image.Image, active: str) -> AsciiGrid:
    width, height = img.size
    pixels = img.load()

    grid: AsciiGrid = []
    for y in range(height):
        row: list[tuple[str, tuple[int, int, int]]] = []
        for x in range(width):
            r, g, b = pixels[x, y]
            brightness = (r + g + b) / 3
            char_idx = 0 if brightness < 128 else len(active) - 1
            row.append((active[char_idx], (r, g, b)))
        grid.append(row)

    return grid


def hue_map(img: Image.Image, active: str) -> AsciiGrid:
    width, height = img.size
    pixels = img.load()

    grid: AsciiGrid = []
    for y in range(height):
        row: list[tuple[str, tuple[int, int, int]]] = []
        for x in range(width):
            r, g, b = pixels[x, y]
            h, _s, _v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            char_idx = int(h * (len(active) - 1))
            row.append((active[char_idx], (r, g, b)))
        grid.append(row)

    return grid


def edge_map(img: Image.Image, active: str) -> AsciiGrid:
    gray = img.convert("L")
    width, height = img.size
    pixels = img.load()
    gray_pixels = gray.load()

    grid: AsciiGrid = []
    for y in range(height):
        row: list[tuple[str, tuple[int, int, int]]] = []
        for x in range(width):
            if x == 0 or x == width - 1 or y == 0 or y == height - 1:
                magnitude = 0
            else:
                gx = (
                    -gray_pixels[x - 1, y - 1] + gray_pixels[x + 1, y - 1]
                    + -2 * gray_pixels[x - 1, y] + 2 * gray_pixels[x + 1, y]
                    + -gray_pixels[x - 1, y + 1] + gray_pixels[x + 1, y + 1]
                )
                gy = (
                    -gray_pixels[x - 1, y - 1] + -2 * gray_pixels[x, y - 1] + -gray_pixels[x + 1, y - 1]
                    + gray_pixels[x - 1, y + 1] + 2 * gray_pixels[x, y + 1] + gray_pixels[x + 1, y + 1]
                )
                magnitude = min(255, int((gx * gx + gy * gy) ** 0.5))
            char_idx = int(magnitude / 255 * (len(active) - 1))
            r, g, b = pixels[x, y]
            row.append((active[char_idx], (r, g, b)))
        grid.append(row)

    return grid
