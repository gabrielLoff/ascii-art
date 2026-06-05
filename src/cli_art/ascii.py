from pathlib import Path

from PIL import Image

CHARS = " .:-=+*#%@"


def image_to_ascii_grid(
    path: str | Path,
    width: int = 80,
    invert: bool = False,
    chars: str | None = None,
) -> list[list[tuple[str, tuple[int, int, int]]]]:
    active = chars if chars is not None else CHARS
    if invert:
        active = active[::-1]

    img = Image.open(path).convert("RGB")
    orig_w, orig_h = img.size
    aspect_ratio = orig_h / orig_w
    height = int(width * aspect_ratio * 0.45)
    img = img.resize((width, height))

    grid: list[list[tuple[str, tuple[int, int, int]]]] = []
    for y in range(height):
        row: list[tuple[str, tuple[int, int, int]]] = []
        for x in range(width):
            r, g, b = img.getpixel((x, y))
            brightness = (r + g + b) / 3
            char_idx = int(brightness / 255 * (len(active) - 1))
            row.append((active[char_idx], (r, g, b)))
        grid.append(row)

    return grid


def render_ansi(grid: list[list[tuple[str, tuple[int, int, int]]]]) -> str:
    lines: list[str] = []
    for row in grid:
        line = ""
        for char, (r, g, b) in row:
            line += f"\033[38;2;{r};{g};{b}m{char}\033[0m"
        lines.append(line)
    return "\n".join(lines)


def render_html(grid: list[list[tuple[str, tuple[int, int, int]]]]) -> str:
    lines = [
        '<!DOCTYPE html>',
        '<html>',
        '<head><meta charset="utf-8"></head>',
        '<body style="background:#000;">',
        '<pre style="color:#fff;line-height:1;font-size:6px;letter-spacing:0;">',
    ]
    for row in grid:
        line = ""
        for char, (r, g, b) in row:
            line += f'<span style="color:rgb({r},{g},{b})">{char}</span>'
        lines.append(line)
    lines.append("</pre>")
    lines.append("</body>")
    lines.append("</html>")
    return "\n".join(lines)
