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


def _escape_xml(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_svg(grid: list[list[tuple[str, tuple[int, int, int]]]]) -> str:
    if not grid or not grid[0]:
        return (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 0 0" width="0" height="0">\n'
            '  <rect width="100%" height="100%" fill="#000" />\n'
            '</svg>'
        )

    font_size = 14
    char_width = 9
    line_height = 16.1
    svg_width = len(grid[0]) * char_width
    svg_height = len(grid) * line_height

    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">',
        '  <rect width="100%" height="100%" fill="#000" />',
        f'  <g font-family="monospace" font-size="{font_size}" xml:space="preserve" style="line-height:1">',
    ]

    for i, row in enumerate(grid):
        y = i * line_height + font_size
        tspans = "".join(
            f'<tspan fill="rgb({r},{g},{b})">{_escape_xml(char)}</tspan>'
            for char, (r, g, b) in row
        )
        lines.append(f'    <text x="0" y="{y:.1f}">{tspans}</text>')

    lines.append("  </g>")
    lines.append("</svg>")
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
